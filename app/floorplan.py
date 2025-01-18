from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Dict
import numpy as np
from PIL import Image
import cv2
import pytesseract
from pydantic import BaseModel

from .logic.pathfind import get_path, initialize_grid
import app.globals as globals
import os

floorplan_router = APIRouter()

# Ensure globals has an 'numpy_image' attribute to store the numpy array
if not hasattr(globals, 'numpy_image'):
    globals.numpy_image = None

if not hasattr(globals, 'coordinates'):
    globals.coordinates = {}

def merge_close_coordinates(detections, threshold=5):
    merged_detections = []
    for icon in detections:
        coord = np.array(icon['coordinates'])
        merged = False
        for existing in merged_detections:
            existing_coord = np.array(existing['coordinates'])
            if np.all(np.abs(coord - existing_coord) <= threshold):
                if icon['confidence'] > existing['confidence']:
                    existing.update(icon)
                merged = True
                break
        if not merged:
            merged_detections.append(icon)
    return merged_detections

def extract_text_with_boxes(image_array: np.ndarray):
    """Extract text and bounding boxes from the image using pytesseract."""
    image = Image.fromarray(image_array)

    # Convert to grayscale and filter non-black pixels
    image_gray = image.convert("L")
    image_array = np.array(image_gray)
    threshold = 50
    filtered_image_array = np.where(image_array < threshold, image_array, 255)
    filtered_image = Image.fromarray(filtered_image_array.astype(np.uint8))

    # Perform OCR
    data = pytesseract.image_to_data(filtered_image, output_type=pytesseract.Output.DICT)

    bounding_boxes = []
    for i in range(len(data['text'])):
        text = data['text'][i]
        try:
            conf = float(data['conf'][i])
            if text.strip() and conf > 50:  # Filter low-confidence text
                x, y, w, h = (data['left'][i], data['top'][i],
                              data['width'][i], data['height'][i])
                # Save coordinates as (x, y, x+w, y+h)
                bounding_boxes.append({
                    'text': text,
                    'coordinates': (int(x), int(y), int(x + w), int(y + h))
                })
        except ValueError:
            continue

    # Combine nearby bounding boxes
    return combine_bounding_boxes(bounding_boxes)

def combine_bounding_boxes(bounding_boxes, distance_threshold=50):
    """Combine bounding boxes that are close to each other."""
    combined_boxes = []
    used = set()

    for i, box1 in enumerate(bounding_boxes):
        if i in used:
            continue
        combined_text = box1['text']
        combined_coords = list(box1['coordinates'])
        used.add(i)

        for j, box2 in enumerate(bounding_boxes):
            if j in used or i == j:
                continue
            if calculate_distance(combined_coords, box2['coordinates']) < distance_threshold:
                combined_text += f" {box2['text']}"
                x1, y1, x2, y2 = combined_coords
                x3, y3, x4, y4 = box2['coordinates']
                combined_coords = [
                    min(x1, x3), 
                    min(y1, y3), 
                    max(x2, x4), 
                    max(y2, y4)
                ]
                used.add(j)

        # Ensure coordinates are native ints
        combined_boxes.append({
            'text': combined_text,
            'coordinates': (int(combined_coords[0]), int(combined_coords[1]), 
                            int(combined_coords[2]), int(combined_coords[3]))
        })

    return combined_boxes

def calculate_distance(box1, box2):
    """Calculate distance between two bounding boxes."""
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    return max(0, max(x3 - x2, x1 - x4)) + max(0, max(y3 - y2, y1 - y4))

class Props(BaseModel):
    description: str
    image_filename: str

@floorplan_router.post("/api/floorplan")
async def floorplan(props: Props) -> JSONResponse:
    description = props.description
    image_filename = props.image_filename

    # Validate the file type
    if not image_filename.endswith(".png"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Only .png files are supported."}
        )

    # Load the image from disk
    image_path = os.path.join("static", "images", "floor", image_filename)
    image = cv2.imread(image_path)

    if image is None:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to open the image at '{image_path}'."}
        )

    # Save image to globals and initialize grid
    globals.numpy_image = image
    initialize_grid(image)

    # Extract dimensions (height and width) as native ints
    height, width = int(image.shape[0]), int(image.shape[1])

    # Convert to grayscale for icon detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Icon detection logic
    base_path = "static/images/icons"
    icon_paths = [
        os.path.join(base_path, f)
        for f in os.listdir(base_path)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ]

    detected_icons = []
    for icon_path in icon_paths:
        icon = cv2.imread(icon_path)
        if icon is None:
            continue
        gray_icon = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_image, gray_icon, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)

        for pt in zip(*locations[::-1]):  # Switch x and y
            confidence = float(result[pt[1], pt[0]])
            # Original box: (x1, y1, x2, y2)
            x1, y1 = pt[0], pt[1]
            x2, y2 = x1 + int(gray_icon.shape[1]), y1 + int(gray_icon.shape[0])

            detected_icons.append({
                "icon_path": os.path.basename(icon_path),
                "coordinates": [int(x1), int(y1), int(x2), int(y2)],  # (x1, y1, x2, y2)
                "confidence": confidence
            })

    filtered_icons = merge_close_coordinates(detected_icons)

    # Text extraction
    combined_bounding_boxes = extract_text_with_boxes(globals.numpy_image)

    # Build icons dictionary in (y1, x1, y2, x2) format
    icons_dict = {}
    for icon in filtered_icons:
        icon_name = os.path.basename(icon['icon_path']).split('.')[0]
        if icon_name not in icons_dict:
            icons_dict[icon_name] = []
        x1, y1, x2, y2 = icon['coordinates']
        # Flip to (y1, x1, y2, x2)
        icons_dict[icon_name].append([int(y1), int(x1), int(y2), int(x2)])

    # Build rooms dictionary in (y1, x1, y2, x2) format
    rooms_dict = {}
    for box in combined_bounding_boxes:
        text_name = box['text']
        if text_name not in rooms_dict:
            rooms_dict[text_name] = []
        x1, y1, x2, y2 = map(int, box['coordinates'])
        # Flip to (y1, x1, y2, x2)
        rooms_dict[text_name].append([int(y1), int(x1), int(y2), int(x2)])

    # Store in globals (all native types)
    response = {
        "icons": icons_dict,  # Already flipped to (y1, x1, y2, x2)
        "rooms": rooms_dict,  # Already flipped to (y1, x1, y2, x2)
        "grid_size": 10,
        "height": height,
        "width": width
    }
    globals.coordinates = response

    # Pathfinding initialization
    img = globals.numpy_image
    grid_size = 10
    final = {}

    # final['icons'] is already in (y1, x1, y2, x2) format (all ints)
    final['icons'] = globals.coordinates["icons"]
    final['height'] = globals.coordinates["height"]
    final['width'] = globals.coordinates["width"]
    final['rooms'] = []

    # For the exit icons, compute midpoints in (row, col) = (y, x)
    if "exit" in final['icons']:
        exit_midpoints = [
            [
                int((bbox[0] + bbox[2]) // 2),  # y midpoint
                int((bbox[1] + bbox[3]) // 2)   # x midpoint
            ]
            for bbox in final['icons']['exit']
        ]
    else:
        exit_midpoints = []

    # Compute midpoints for each room bounding box and run pathfinding
    for room_name, boxes in globals.coordinates["rooms"].items():
        for bbox in boxes:
            # bbox is in (y1, x1, y2, x2)
            y_mid = int((bbox[0] + bbox[2]) // 2)
            x_mid = int((bbox[1] + bbox[3]) // 2)
            # Call get_path with (y, x) for both start and exit midpoints.
            cost, route = get_path(img, (y_mid, x_mid), exit_midpoints, grid_size, False)
            # Convert route coordinates into native ints
            route_converted = [[int(point[0]), int(point[1])] for point in route]
            final['rooms'].append({
                "name": str(room_name),
                "text_bounding_box_coords": [int(coord) for coord in bbox],
                "route": route_converted
            })

    return JSONResponse(content=final)


'''
final = {
    "icons": {
        # Same structure as globals.coordinates["icons"]
        # For example:
        "exit": List[List[int]],              # List of exit icon boxes in [y1, x1, y2, x2] format
        "exit_lift": List[List[int]],         # etc.
        "extinguisher_powder": List[List[int]],
        # ... additional icons ...
    },
    "height": int,       # Height of the floor image (in pixels)
    "width": int,        # Width of the floor image (in pixels)
    "rooms": [
        {
            "name": str,                             # The room name (e.g., "Hospital Level 5")
            "text_bounding_box_coords": List[int],   # The room bounding box as [y1, x1, y2, x2]
            "route": List[List[int]]                   # The computed route. Each point in the route is a list [y, x]
        },
        # ... one dictionary for each room bounding box processed ...
    ]
}
'''
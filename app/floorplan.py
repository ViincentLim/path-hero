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
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                bounding_boxes.append({'text': text, 'coordinates': (x, y, x + w, y + h)})
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
                combined_coords = [min(x1, x3), min(y1, y3), max(x2, x4), max(y2, y4)]
                used.add(j)

        combined_boxes.append({'text': combined_text, 'coordinates': tuple(combined_coords)})

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
async def floorplan(
        props: Props,
    # description: str = Form(...),
    # image_filename: str = Form(...)
    # # image_file: UploadFile = Form(...)
) -> JSONResponse:
    description = props.description
    image_filename = props.image_filename
    print(description)
    print(image_filename)
    # Validate the file type
    if not image_filename.endswith(".png"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Only .png files are supported."}
        )

    # Read the uploaded file as a numpy array
    image = cv2.imread("static/images/floor/" + image_filename)
    cv2.imshow("", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # image_array = np.frombuffer(await image_file.read(), np.uint8)
    # image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Failed to process the image. Please try again."}
        )

    # Save the numpy array and grid to globals
    globals.numpy_image = image
    initialize_grid(image)

    # Extract dimensions (height and width)
    height, width = image.shape[:2]

    # Convert to grayscale for icon detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Icon detection logic
    base_path = "static/images/icons"  # Update to your icon folder path
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
            confidence = result[pt[1], pt[0]]
            detected_icons.append({
                "icon_path": os.path.basename(icon_path),
                "coordinates": list(map(int, (pt[0], pt[1], pt[0] + gray_icon.shape[1], pt[1] + gray_icon.shape[0]))),  # Ensure integers
                "confidence": float(confidence)  # Convert to float
            })

    filtered_icons = merge_close_coordinates(detected_icons)

    # Text extraction logic
    combined_bounding_boxes = extract_text_with_boxes(globals.numpy_image)

    # Format the response
    icons_dict = {}
    for icon in filtered_icons:
        icon_name = os.path.basename(icon['icon_path']).split('.')[0]
        if icon_name not in icons_dict:
            icons_dict[icon_name] = []
        icons_dict[icon_name].append(icon['coordinates'])

    rooms_dict = {}
    for box in combined_bounding_boxes:
        text_name = box['text']
        if text_name not in rooms_dict:
            rooms_dict[text_name] = []
        # Convert coordinates to Python int
        rooms_dict[text_name].append(list(map(int, box['coordinates'])))

    # Add height and width to the response
    response = {
        "icons": icons_dict,
        "rooms": rooms_dict,
        "grid_size": 10,  # Ensure this is a Python int
        "height": height,
        "width": width
    }

    globals.coordinates = response

    #inital pathfinding
    img = globals.numpy_image
    goals = globals.coordinates['icons']['exit']
    grid_size = 10

    final = {}
    final['icons'] = globals.coordinates["icons"]
    final['height'] = globals.coordinates["height"]
    final['width'] = globals.coordinates["width"]
    final['rooms'] = []

    for start_room_names, values in globals.coordinates["rooms"].items():
        for value in values:
            midpoint = ((value[0] + value[2]) // 2, (value[1] + value[3]) // 2)
            _, route = get_path(img, midpoint, goals, grid_size, False) # false for manhattan distance heuristic
            final['rooms'].append({
                "name" : start_room_names,
                "text_bounding_box_coords": value, #guarnteed to be unique
                "route": route
                })

    return JSONResponse(content=final)

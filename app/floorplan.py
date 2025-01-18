from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Union
import numpy as np
from PIL import Image

floorplan_router  = APIRouter()

@floorplan_router.post("/api/floorplan")
async def floorplan(
    file_name: str = Form(...),
    image_file: UploadFile = Form(...)
) -> JSONResponse:
    # Validate the file type
    if not image_file.filename.endswith(".png"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Only .png files are supported."}
        )

    # Load and preprocess the image
    image = Image.open(image_file.file).convert("RGB")  # Convert to RGB for consistent pixel handling
    grid_size = 10  # Example grid size
    image_array = np.array(image)

    # Example preprocessing to identify features (replace with actual logic)
    fire_extinguishers = [[10, 15], [20, 25]]  # Placeholder for detected fire extinguisher coordinates
    exits = [[50, 50], [100, 150]]  # Placeholder for detected exit coordinates
    rooms = [
        {
            "room_id": "Room 1",
            "bounding_box_coords": [[5, 10], [5, 11], [6, 10], [6, 11]],
            "route": [[5, 11], [6, 12], [7, 13], [8, 14], [9, 15], [10, 16]]
        },
        {
            "room_id": "Room 2",
            "bounding_box_coords": [[25, 30], [25, 31], [26, 30], [26, 31]],
            "route": [[25, 31], [26, 32], [27, 33], [28, 34], [29, 35], [30, 36]]
        }
    ]

    # Example response
    response = {
        "fire_extinguishers": fire_extinguishers,
        "exits": exits,
        "rooms": rooms,
        "grid_size": grid_size
    }

    return JSONResponse(content=response)

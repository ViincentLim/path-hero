# numpy_image is a BGR array

def init():
    global numpy_image
    global coordinates
    global grid
    numpy_image = []
    coordinates = {}
    grid = None

'''
globals.coordinates = {
    "icons": {
        "exit": List[List[int]],              # List of exit icons, each as [y1, x1, y2, x2]
        "exit_lift": List[List[int]],         # List of exit lift icons as [y1, x1, y2, x2]
        "extinguisher_powder": List[List[int]],  # List of powder extinguisher icons as [y1, x1, y2, x2]
        # ... other icon keys ...
    },
    "rooms": {
        "Hospital Level 5": List[List[int]],  # List of bounding box(es) for this room, each as [y1, x1, y2, x2]
        "Bed Lift": List[List[int]],          # List of bounding box(es) for room "Bed Lift"
        "Drug store": List[List[int]],        # ...
        "AHU": List[List[int]],
        "8-bedded ward": List[List[int]],
        "Toilet": List[List[int]],
        # ... additional room names ...
    },
    "grid_size": int,  # Grid size used for pathfinding (e.g., 10)
    "height": int,     # Height of the processed floor image in pixels
    "width": int       # Width of the processed floor image in pixels
}
'''
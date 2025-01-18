# numpy_image is a BGR array

'''
coordinates Field
Type: List[List[int]]
Format: Each bounding box is represented as a list of four integers: [x_min, y_min, x_max, y_max].
Example:
json
Edit
"coordinates": [x_min, y_min, x_max, y_max]
x_min: Horizontal coordinate of the top-left corner.
y_min: Vertical coordinate of the top-left corner.
x_max: Horizontal coordinate of the bottom-right corner.
y_max: Vertical coordinate of the bottom-right corner.
This format specifies a rectangular area in the image.

Specific Use Cases
1. icons
Icons refer to specific detected objects like exit, hosereel, or extinguisher_co2. Each icon name maps to an array of bounding boxes.

Type: Dict[str, List[List[int]]]

Format:

json
Edit
"icons": {
    "icon_name": [
        [x_min, y_min, x_max, y_max],
        ...
    ]
}
Explanation: Each key (icon_name) represents a type of icon, and its value is a list of bounding boxes where instances of this icon were detected.

Example:

json
Copy
Edit
"icons": {
    "exit": [[307, 796, 383, 871], [1729, 814, 1805, 889]]
}
First Box: exit at coordinates [307, 796, 383, 871]
Top-left: (307, 796)
Bottom-right: (383, 871)
Second Box: exit at coordinates [1729, 814, 1805, 889]
2. rooms
Rooms refer to labeled regions in the image, such as Hospital Level 5, Drug store, or Toilet. Each room name maps to an array of bounding boxes.

Type: Dict[str, List[List[int]]]

Format:

json
Edit
"rooms": {
    "room_name": [
        [x_min, y_min, x_max, y_max],
        ...
    ]
}
Explanation: Each key (room_name) represents a labeled area in the image, and its value is a list of bounding boxes marking detected areas.

Example:

json
Edit
"rooms": {
    "Hospital Level 5": [[717, 32, 1287, 101]],
    "Toilet": [[1319, 460, 1398, 483]]
}
First Box: Hospital Level 5 at coordinates [717, 32, 1287, 101]
Top-left: (717, 32)
Bottom-right: (1287, 101)
Second Box: Toilet at coordinates [1319, 460, 1398, 483]
Coordinate System
1. Origin
The coordinate system originates from the top-left corner of the image.
(x_min, y_min) represents the top-left corner of a box.
(x_max, y_max) represents the bottom-right corner of a box.
2. Units
The units are in pixels.
3. Image Dimensions
height: Total number of rows (pixels).
width: Total number of columns (pixels).
Example:
Given height = 1414 and width = 2000, the top-left corner of the image is (0, 0), and the bottom-right corner is (2000, 1414).
'''

def init():
    global numpy_image
    global coordinates
    global grid
    numpy_image = []
    coordinates = {}
    grid = None
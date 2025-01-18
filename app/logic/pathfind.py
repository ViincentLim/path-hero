# Path finding logic to be used in both endpoints
import cv2
import heapq
import numpy as np

from filter_walls import filter_walls_as_image

from PIL import Image
from typing import Tuple, List, Optional, Dict

def convert_image_to_grid(
    image: Image.Image,
    grid_size: int
) -> List[List[int]]:
    """
    Convert a cleaned image into a grid representation.

    Args:
        image: Cleaned input image as a PIL Image.
        grid_size: Size of each grid cell in pixels.

    Returns:
        2D grid where 1 represents traversable space, and 0 represents obstacles.
    """
    image_array = np.array(image)  # Convert to NumPy array
    rows, cols = image_array.shape[:2]
    
    # Calculate the grid dimensions
    grid_rows = rows // grid_size
    grid_cols = cols // grid_size

    # Initialize the grid
    grid = np.zeros((grid_rows, grid_cols), dtype=int)

    # Fill the grid: A cell is traversable (1) if all its pixels are white
    for i in range(grid_rows):
        for j in range(grid_cols):
            sub_region = image_array[
                i * grid_size : (i + 1) * grid_size,
                j * grid_size : (j + 1) * grid_size
            ]
            # Check if all pixels are white (255, 255, 255)
            if np.all(sub_region == 255):
                grid[i, j] = 1  # Traversable

    return grid.tolist()

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Calculate the Manhattan distance between two points a and b.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_pathfinding(
    grid: List[List[int]],
    start: Tuple[int, int],
    goals: List[Tuple[int, int]],
    fire_coords: Optional[List[Tuple[int, int]]] = None
) -> List[Tuple[int, int]]:
    """
    A* pathfinding algorithm to find the shortest path from start to the nearest goal.

    Args:
        grid: 2D grid representation of the map (0 = obstacle, 1 = traversable).
        start: Starting coordinate (x, y).
        goals: List of goal coordinates [(x1, y1), (x2, y2), ...].
        fire_coords: Optional list of fire coordinates [(fx1, fy1), (fx2, fy2), ...].

    Returns:
        List of coordinates representing the shortest path from start to the nearest goal.
    """
    rows, cols = len(grid), len(grid[0])

    def is_within_bounds(coord):
        x, y = coord
        return 0 <= x < rows and 0 <= y < cols

    def is_traversable(coord):
        x, y = coord
        return grid[x][y] == 1

    open_set = []
    heapq.heappush(open_set, (0, start))  # Priority queue with (cost, coordinate)

    came_from = {}
    g_score = {start: 0}
    f_score = {start: min(heuristic(start, goal) for goal in goals)}

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

    while open_set:
        _, current = heapq.heappop(open_set)

        # Check if the current node is one of the goals
        if current in goals:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Reverse to get path from start to goal

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if not is_within_bounds(neighbor) or not is_traversable(neighbor):
                continue

            if fire_coords and neighbor in fire_coords:
                continue  # Avoid fire cells

            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + min(heuristic(neighbor, goal) for goal in goals)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Return an empty path if no path to any goal is found



img_path = r"C:\Users\rithi\Documents\GitHub\path-hero\static\images\floor\cleaned_image.jpg"
image = cv2.imread(img_path)
grid_size = 10

grid = convert_image_to_grid(image, grid_size)
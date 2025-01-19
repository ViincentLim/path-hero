# Path finding logic to be used in both endpoints
import heapq
import numpy as np
import app.globals as globals

from app.logic.filter_walls import filter_walls_as_image

from PIL import Image
from typing import Tuple, List, Optional, Dict, Any


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

def heuristic_manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Calculate the Manhattan distance between two points a and b.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic_fire(a: Tuple[int, int], b: Tuple[int, int], fire_coords: Optional[List[Tuple[int, int]]] = None) -> int:
    """
    Calculate the Manhattan distance between two points a and b, with a penalty for proximity to fire coordinates.
    """
    base_distance = abs(a[0] - b[0]) + abs(a[1] - b[1])
    penalty = 0

    if fire_coords:
        for fx, fy in fire_coords:
            fire_distance = abs(a[0] - fx) + abs(a[1] - fy)
            penalty += max(0, (20 - fire_distance) ** 2)
            if fire_distance < 50:  # Threshold (adjust as needed)
                penalty += 1e12

    return base_distance + penalty

def pixel_to_grid(pixel_coord: Tuple[int, int], grid_size: int) -> Tuple[int, int]:
    """
    Convert pixel coordinates to grid coordinates.
    """
    return pixel_coord[0] // grid_size, pixel_coord[1] // grid_size

def grid_to_pixel(grid_coord: Tuple[int, int], grid_size: int) -> Tuple[int, int]:
    """
    Convert grid coordinates to pixel coordinates (center of the grid cell).
    """
    return grid_coord[0] * grid_size + grid_size // 2, grid_coord[1] * grid_size + grid_size // 2


def a_star_pathfinding(
    grid: List[List[int]],
    start: Tuple[int, int],
    goals: List[Tuple[int, int]],
    heuristic: bool, # true means heuristic_fire, false means heuristic_manhattan
    fire_coords: Optional[List[Tuple[int, int]]] = None
) -> tuple[float, list[Any]]:
    """
    A* pathfinding algorithm to find the shortest path from start to the nearest goal.

    Args:
        grid: 2D grid representation of the map (0 = obstacle, 1 = traversable).
        start: Starting coordinate (x, y).
        goals: List of goal coordinates [(x1, y1), (x2, y2), ...].
        heuristic: Boolean to determine heuristic function to use for pathfinding.
        fire_coords: Optional list of fire coordinates [(fx1, fy1), (fx2, fy2), ...].

    Returns:
        List of coordinates representing the shortest path from start to the nearest goal.
    """
    rows, cols = len(grid), len(grid[0])

    if fire_coords:
        grid = mark_fire_zones(grid, fire_coords, fire_proximity_threshold=150, fire_size="s", grid_size=10)

    def is_within_bounds(coord):
        x, y = coord
        return 0 <= x < rows and 0 <= y < cols

    def is_traversable(coord):
        x, y = coord
        return grid[x][y] == 1

    open_set = []
    heapq.heappush(open_set, (0, start))  # Priority queue with (cost, coordinate)

    heuristic_func = heuristic_fire if heuristic else heuristic_manhattan
    came_from = {}
    g_score = {start: 0}
    f_score = {start: min(heuristic_func(start, goal) for goal in goals)}

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
            return g_score[current], path[::-1]  # Reverse to get path from start to goal

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
                f_score[neighbor] = tentative_g_score + min(heuristic_func(neighbor, goal) for goal in goals)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return float('inf'), []  # Return an empty path if no path to any goal is found

def initialize_grid(img, grid_size=10):
    image = filter_walls_as_image(img)
    globals.grid = convert_image_to_grid(image, grid_size)

# PLease let Vincent know and update /api/fire when grid_size changes
def get_path(img, start, goals, grid_size=10, heuristic_func=heuristic_manhattan):
    # Visualize the grid
    # plt.imshow(grid, cmap='gray')
    # plt.title("Converted Grid")
    # plt.show()

    # start = (500, 1100)
    # goals = [(766, 359), (850, 1500)]

    # Convert start and goals to grid coordinates
    start_grid = pixel_to_grid(start, grid_size)
    goals_grid = [pixel_to_grid(goal, grid_size) for goal in goals]
    # print("Start (grid):", start_grid)
    # print("Goals (grid):", goals_grid)

    distance, optimal_path_grid = a_star_pathfinding(globals.grid, start_grid, goals_grid, heuristic_func)

    # Visualize the path on the grid
    optimal_path_pixels = [grid_to_pixel(coord, grid_size) for coord in optimal_path_grid]
    # for (x, y) in path_pixels:
    #     cv2.circle(image, (y, x), radius=2, color=(0, 0, 255), thickness=-1)

    # plt.imshow(image)
    # plt.title("A* Pathfinding Path")
    # plt.show()
    return distance, optimal_path_pixels

#===============================================================================================
def mark_fire_zones(
    grid: List[List[int]],
    fire_coords: List[Tuple[int, int]],
    fire_proximity_threshold: int,
    fire_size: str,
    grid_size: int
) -> List[List[int]]:
    """
    Mark fire-affected zones in the grid as non-traversable.

    Args:
        grid: 2D grid representation of the map.
        fire_coords: List of fire coordinates [(fx1, fy1), (fx2, fy2), ...].
        fire_proximity_threshold: Distance from the fire center to mark as dangerous.
        fire_size: Size of the fire ("s" for small, "l" for large).
        grid_size: Size of each grid cell in pixels.

    Returns:
        Updated grid with fire zones marked as non-traversable (0).
    """
    fire_radius = fire_proximity_threshold // grid_size
    if fire_size == "l":
        fire_radius *= 2  # Increase radius for large fires

    rows, cols = len(grid), len(grid[0])
    for fx, fy in fire_coords:
        fx_grid, fy_grid = fx // grid_size, fy // grid_size  # Map fire coords to grid
        for i in range(max(0, fx_grid - fire_radius), min(rows, fx_grid + fire_radius + 1)):
            for j in range(max(0, fy_grid - fire_radius), min(cols, fy_grid + fire_radius + 1)):
                # Mark cells within the fire radius as non-traversable
                if (i - fx_grid) ** 2 + (j - fy_grid) ** 2 <= fire_radius ** 2:
                    grid[i][j] = 0

    return grid
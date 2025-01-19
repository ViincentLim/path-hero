import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

import app.globals as globals
from app.logic.llm.recommendation import recommend, FireRecommendations
from app.logic.pathfind import get_path, heuristic_fire, a_star_pathfinding, pixel_to_grid, grid_to_pixel
from app.logic.pathfind import get_path, heuristic_fire, a_star_pathfinding, pixel_to_grid, grid_to_pixel

fire_router = APIRouter()


class Props(BaseModel):
    coordinates: list[tuple[float, float]]
    description: str


def merge_lines_in_path(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if len(path) == 0:
        return []
    elif len(path) == 1 or len(path) == 2:
        return path

    result = [path[0]]
    for i in range(1, len(path) - 1):
        if result[-1][0] == path[i][0] and path[i][0] == path[i + 1][0]:
            continue
        elif result[-1][1] == path[i][1] and path[i][1] == path[i + 1][1]:
            continue
        else:
            result.append(path[i])
    result.append(path[-1])
    return result


@fire_router.post("/api/fire")
async def fire(props: Props):
    """
    :param coordinates: list of fire coordinates in (x,y) format, with origin in the top left corner
    :param description: llm prompt to describe the fire
    :return:
    """
    # globals.numpy_image
    # globals.coordinates
    # globals.grid
    # Should be y, x
    fire_coordinate: tuple[int, int] = (int(props.coordinates[0][0]), int(props.coordinates[0][1]))
    recommendation: FireRecommendations = await recommend(image=globals.numpy_image, fire_coordinate=fire_coordinate)
    routes: list[list[tuple[int, int]]] = []
    for instruction_path in recommendation.instruction_paths:
        # If the instruction_path has 1 or 0 elements, no actual path needed
        if len(instruction_path) < 2:
            routes.append([])
            continue

        accumulated_pixel_path: list[tuple[int, int]] = []

        # build the route segment by segment, e.g.:
        # if instruction_path == ["exit", "Toilet", "exit"]
        # segment 1 = ("exit", "Toilet"), segment 2 = ("Toilet", "exit")
        number_of_routes = len(instruction_path) - 1

        for i in range(number_of_routes):
            start_label = instruction_path[i]
            end_label   = instruction_path[i + 1]

            all_possible_start = []
            if start_label in globals.coordinates["icons"]:
                all_possible_start = globals.coordinates["icons"][start_label]
            elif start_label in globals.coordinates["rooms"]:
                all_possible_start = globals.coordinates["rooms"][start_label]

            all_possible_end = []
            if end_label in globals.coordinates["icons"]:
                all_possible_end = globals.coordinates["icons"][end_label]
            elif end_label in globals.coordinates["rooms"]:
                all_possible_end = globals.coordinates["rooms"][end_label]

            # If either start or end doesn't exist in our mapping, skip
            if not all_possible_start or not all_possible_end:
                continue

            # Prepare arrays to keep track of all route distances
            current_possible_distances = np.full(
                (len(all_possible_start), len(all_possible_end)), np.inf
            )
            current_possible_routes = np.empty(
                (len(all_possible_start), len(all_possible_end)), dtype=object
            )

            # For each possible start-end pair, run A* to find a path
            for j, possible_start in enumerate(all_possible_start):
                for k, possible_end in enumerate(all_possible_end):
                    start_grid = pixel_to_grid((possible_start[0], possible_start[1]), grid_size=10)
                    end_grid   = pixel_to_grid((possible_end[0], possible_end[1]), grid_size=10)

                    distance, route_grid = a_star_pathfinding(
                        globals.grid,
                        start_grid,
                        [end_grid],
                        heuristic=True,
                        fire_coords=[fire_coordinate]
                    )

                    current_possible_distances[j, k] = distance
                    current_possible_routes[j, k] = route_grid

            # Select the minimum distance route among all possible combos
            min_index = np.argmin(current_possible_distances)
            row, col = np.unravel_index(min_index, current_possible_distances.shape)
            best_distance = current_possible_distances[row, col]
            best_route_grid = current_possible_routes[row, col]

            if best_distance == float("inf") or not best_route_grid:
                # No path found among any start-end combos
                continue

            best_route_pixels = [grid_to_pixel(rc, 10) for rc in best_route_grid]

            # Concatenate this segment route into accumulated path
            if i == 0:
                # First segment: add everything
                accumulated_pixel_path.extend(best_route_pixels)
            else:
                # If continuing from the last segment, skip the first node
                # to avoid duplication, because it should match the end of the previous segment
                accumulated_pixel_path.extend(best_route_pixels[1:])

        # Optionally merge collinear segments to reduce unneeded waypoints
        merged_path = merge_lines_in_path(accumulated_pixel_path)
        routes.append(merged_path)

    return {
        "instructions": recommendation.instructions,
        "routes": routes,
        "class_of_fire": recommendation.class_of_fire,
        "instruction_paths": recommendation.instruction_paths
    }

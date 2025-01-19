import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

import app.globals as globals
from app.logic.llm.recommendation import recommend, FireRecommendations
from app.logic.pathfind import get_path, heuristic_fire, a_star_pathfinding, pixel_to_grid

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
        routes.append([])
        # Example: instruction_path = ['exit', 'Toilet', 'exit']
        if len(instruction_path) > 1:
            number_of_routes = len(instruction_path) - 1
            possible_routes = []
            possible_distances = []
            for i in range(number_of_routes):
                [start, end] = instruction_path[i:i + 2]
                all_possible_start = []
                if start in globals.coordinates['icons']:
                    all_possible_start = globals.coordinates['icons'][start]
                elif start in globals.coordinates['rooms']:
                    all_possible_start = globals.coordinates['rooms'][start]

                all_possible_end = []
                if end in globals.coordinates['icons']:
                    all_possible_end = globals.coordinates['icons'][end]
                elif end in globals.coordinates['rooms']:
                    all_possible_end = globals.coordinates['rooms'][end]

                # HACK START
                possible_start_tuple = (all_possible_start[0][0], all_possible_start[0][1])
                possible_end_tuple = (all_possible_end[0][0], all_possible_end[0][1])
                distance, optimal_path = a_star_pathfinding(globals.grid,
                                                            pixel_to_grid(possible_start_tuple, grid_size=10),
                                                            [pixel_to_grid(possible_end_tuple, grid_size=10)],
                                                            heuristic=True, fire_coords=[fire_coordinate])
                routes[-1].extend(merge_lines_in_path(optimal_path))
                # HACK END

                # TODO: fill all possible start and end
                # # globals.coordinates['icons']
                # # globals.coordinates['rooms']
                # current_possible_distances = np.full((len(all_possible_start), len(all_possible_end)), np.inf)
                # current_possible_routes = np.empty(shape=(len(all_possible_start), len(all_possible_end)), dtype=object)
                # for j, possible_start in enumerate(all_possible_start):
                #     for k, possible_end in enumerate(all_possible_end):
                #         possible_start_tuple = (possible_start[0], possible_start[1])
                #         possible_end_tuple = (possible_end[0], possible_end[1])
                #         (distance, route) = get_path(globals.numpy_image, possible_start_tuple, [possible_end_tuple])
                #         # (distance, route) = a_star_pathfinding(globals.grid, pixel_to_grid(possible_start_tuple, grid_size=10), [pixel_to_grid(possible_end_tuple, grid_size=10)], heuristic=True, fire_coords=[fire_coordinate])
                #         if distance == float('inf'):
                #             print("this gives inf", possible_start_tuple, possible_end_tuple)
                #         print('distance:', distance)
                #         current_possible_routes[j, k] = route
                #         current_possible_distances[j, k] = distance
                # if i == 0:
                #     print(current_possible_distances)
                #     print("\n")
                #
                # # current_possible_routes[:, 0] = start
                # # print(start, end)
                # possible_distances.append(current_possible_distances)
                # possible_routes.append(current_possible_routes)

    return {"instructions": recommendation.instructions, "routes": routes}

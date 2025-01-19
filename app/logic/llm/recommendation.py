import os
from enum import Enum

import cv2
from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel

POSSIBLE_POINTS = [
    'exit',
    'exit_lift',
    'extinguisher_co2',
    'extinguisher_foam',
    'extinguisher_powder',
    'extinguisher_water',
    'hosereel'
]


class ClassOfFire(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'


class Step(BaseModel):
    text: str
    path: list[str | None]


class FireRecommendations(BaseModel):
    instructions: list[str]
    instruction_paths: list[list[str]]
    fire_location: str
    class_of_fire: str
    object_on_fire: str


async def recommend(image: cv2.typing.MatLike, fire_coordinate: tuple[int, int]) -> FireRecommendations:
    """Use it like this: recommend(cv2.imread('static/images/floor/hospital_simple.png'), (y, x))"""
    """If you already have a cv2_image, use: recommend(cv2_image, (y, x))"""
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    # Convert cv2 image from BGR to RGB, then cast it to PIL image for gemini api
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    fire_image_path = "static/images/fire.png"
    fire_image = Image.open(fire_image_path)
    image.paste(fire_image, (fire_coordinate[1] - fire_image.height // 2, fire_coordinate[0] - fire_image.width // 2))
    # image.show()

    prompt = f"""
    Find the location of the fire in the image.
    Output object on fire. If no info given, consider what is likely to catch fire in the location.
    Output the class of fire. if it is unknown, consider what class the object is ('A' if have plenty of solids like paper, 'B' if the room has flammable liquid, etc). 
    Give me a list of instructions for firefighting, along with the list of paths to take for each respective instruction (EMPTY list with 0 elements if this step does not require a path).
    Example (for this example, the fire is in drug store):
    // IMPORTANT: Explain the reasoning behind each step in detail (more detailed than my example if possible)
    instructions: [
        "Send 2 people to search for casualties in drug store.",
        "Once they find the casualties, evacuate them to the nearest exit.",
        "Send 2 people concurrently to extinguish the fire with a foam extinguisher.",
        "If extinguisher runs out before putting out the fire, leave the room.",
        "Send 2 people to search the adjacent toilet for casualties, bringing the key to unlock the toilet cubicle.",
        "If there are any casualties, evacuate them.",
        "Send 8 people to search casualties in Room A, each bed in pairs, transferring them to wheelchairs and setting up mobile life-support apparatus to those under life-support.",
        "Evacuate them to the nearest exit.",
        "Send 3 people to don up fire suits and breathing apparatus.",
        "Send those 3 people to set up hose to the fire location and attack the fire, replacing the previous firefighters with extinguishers.",
        "Send 2 people to set up hose to the fire location and do boundary cooling at the adjacent toilet on the wall adjacent to the drug store.",
    ]
    // Possible points for path: {POSSIBLE_POINTS} or the respective room name (exact spelling and capitalization)
    instruction_paths: [
        ["exit", "extinguisher_foam", "Drug Store"],
        ["Drug Store", "exit"],
        ["exit", "extinguisher_foam", "Drug Store"],
        ["Drug Store", "exit"],
        ["exit", "Toilet"],
        ["Toilet", "exit"],
        ["exit", "Room A"],
        ["Room A", "exit"],
        [], // EMPTY list as no movement required for donning
        ["exit", "hosereel", "Drug Store"],
        ["exit", "hosereel", "Toilet"],
    ]
    
    
    Recommendation:
    - Rescue First: Prioritize occupant rescue. Medical staff should prepare non-ambulant patients with wheelchairs or mobile life support if needed
    - Put out the fire with extinguisher in the location of the fire first.
    - Pick the extinguisher or hosereel first before entering room
    - In a room with electrical appliances, isolate power first
    - When people who aren't already on the floor enter the floor, starting point is an exit
    - When evacuating, final destination is always an exit
    - In server rooms or areas with high electrical loads, isolate electrical panels before suppressing fires. Use CO₂ or clean agent extinguishers, never water to prevent equipment damage.
    - Implement a ‘divide and conquer’ strategy—assign teams to both fire suppression and occupant evacuation concurrently.
    - Use the buddy system. No firefighter should operate alone inside hazardous zones
    - Use the correct extinguishing agent: Water for Class A fires, foam for flammable liquids (Class B), CO₂/dry chemical for electrical fires (Class C)
    - For locked or secured compartments, carry forcible entry tools (halligan bar, axe) in addition to master keys to ensure rapid access.
    - For gas leaks on fire, do not extinguish the flame until the gas supply is isolated to prevent uncontrolled vapor release.
    - Apply horizontal evacuation first in hospitals—move patients to adjacent fire-safe compartments before vertical evacuation. If there is a bed lift, use it for bed-bound casualties instead of other exits.
    - Try to extinguish the fire with the corresponding extinguisher first
    - Coordinate ventilation with fire attack teams to prevent worsening fire spread. Ventilate only when water is ready to be applied
    - Don up fire suits and breathing apparatus if expected to spend time in smoke
    - Search adjacent compartments for casualties and evacuate them
        a. prioritize the higher risks locations and explain why you prioritise them clearly!!
        b. cool the adjacent compartments if the manpower allows
    - In kitchens, turn off gas supply valves immediately to prevent gas-fed fires before attempting to extinguish flames
    - In medical storage rooms, identify and isolate oxygen tanks or medical gases to prevent explosions
    """
    response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=[image, prompt],
                                              config=types.GenerateContentConfig(
                                                  response_mime_type="application/json",
                                                  response_schema=FireRecommendations,
                                                  temperature=1.3
                                              ))
    # return response.text
    return FireRecommendations.model_validate_json(response.text)

import base64
import json
import os
from enum import Enum

from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel, parse_obj_as

class Point(str, Enum):
    exit = 'exit'
    exit_lift = 'exit_lift'
    extinguisher_co2 = 'extinguisher_co2'
    extinguisher_foam = 'extinguisher_foam'
    extinguisher_powder = 'extinguisher_powder'
    extinguisher_water = 'extinguisher_water'
    hosereel = 'hosereel'

class Step(BaseModel):
    text: str
    path: list[Point]

class FireRecommendations(BaseModel):
    instructions: list[str]
    fire_locations: list[str]

def recommend() -> FireRecommendations:
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    img_path = 'static/images/floor/hospital_simple.png'
    image = Image.open(img_path)

    prompt = "Find the location of the fire. give me a list of instructions for firefighting."
    response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=[image, prompt],
                                              config=types.GenerateContentConfig(
                                                  response_mime_type="application/json",
                                                  response_schema=FireRecommendations,
                                              ), )
    return FireRecommendations.model_validate_json(response.text)

import cv2
from fastapi import FastAPI
from dotenv import load_dotenv
from app.floorplan import floorplan_router
from app.fire import fire_router
from app.logic.llm.recommendation import recommend

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World",
            "ahu_fire": await recommend(cv2.imread('static/images/floor/hospital_simple.png'), (248, 1790)),
            "8-bedded": await recommend(cv2.imread('static/images/floor/hospital_simple.png'), (1414-1122, 1196)),
            }

app.include_router(floorplan_router)
app.include_router(fire_router)
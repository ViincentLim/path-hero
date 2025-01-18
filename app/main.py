from fastapi import FastAPI
from dotenv import load_dotenv
from floorplan import floorplan_router
from fire import fire_router

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(floorplan_router)
app.include_router(fire_router)
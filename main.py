import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import subway_updater
from routers import chatbot

load_dotenv()

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://mindhive-assessement-frontend.onrender.com/",
    "http://localhost:8000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Only allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(subway_updater.router)
app.include_router(chatbot.router)


@app.get("/test")
def read_root():
    return {"Hello": "World"}


@app.get("/getAllKLSubway")
def get_all_kl_subway():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DBNAME")
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subway_branches")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return JSONResponse(content=data)
import requests
import json
import re
import os
import mysql.connector
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import APIRouter

router = APIRouter()
load_dotenv()

@router.get("/gemmaSendMsg")
def update_subway_branches():
    try:
        # TODO: EITHER GET ALL HERE OR POST DATA BACK FOR LLM TO FILTER

        branch_info = "\n".join([
                f"- {b['name']} at ({b['latitude']}, {b['longitude']})"
                for b in branches
            ])
            
        prompt=f"""
            You are a helpful assistant that helps users find Subway restaurant branches near them.

            User's current location: ({user_location['latitude']}, {user_location['longitude']})

            Here is a list of available Subway branches:
            {branch_info}

            User asked: "{user_question}"

            Respond with the most helpful answer, and suggest the closest relevant branches if location-based.
        """




        response = requests.post(
            url=os.getenv("OPENROUTER_URL"),
            headers={
                "Authorization": f"Bearer {os.getenv("OPENROUTER_KEY")}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemma-3-4b-it:free",
                "messages": [{
                    "role": "user",
                    "content": [{ "type": "text", "text": prompt }]
                }],
                
            })
        )

        reply = response.json()["choices"][0]["message"]["content"]
        return {
            "status": "success", 
            "gemmaReply": reply,
            "newOrder": []
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
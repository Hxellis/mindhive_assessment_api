import requests
import json
import re
import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()
load_dotenv()

class Message(BaseModel):
    center: object
    question: str
    branches: list

@router.post("/chatbotSendMsg")
def chatbot_send_message(body: Message):
    try:            
        # a LLM is propmting for a LLM
        prompt = f"""
        You are a helpful assistant that helps users find Subway restaurant branches near them and answer relevant questions about Subway branches in Kuala Lumpur.

        User's current location: ({body.center['lat']}, {body.center['lng']}).

        Here is a list of available Subway branches:
        {json.dumps(body.branches, indent=2)}

        User asked: "{body.question}"

        Your task:

        - Understand the user's intent and determine whether the question is about:
            • Branch count in a specific area (e.g. "How many branches are in Bangsar")
            • Proximity to a location (e.g. "Which is closest to KLCC")
            • Operating hours (e.g. "Which branch opens latest?")
            • General branch info

        - If the question is **location-related**, use the branch addresses to infer geography:
            • All locations will be within Kuala Lumpur, Malaysia.
            • Use geolocation reasoning to include branches in or near the named area.
            • Do NOT rely only on keyword string matching — include nearby neighborhoods or known malls/landmarks if relevant.
            • For example, include "KL Gateway" when user asks about "Bangsar South".

        - If the question is about **opening/closing times**, sort the branches in `newOrder` accordingly.
            • For example, "Which closes the latest?" → sort by closing time descending.
            • Be flexible in interpreting opening hours phrasing.

        - Always include a helpful `reply` summarizing your answer (e.g. how many relevant branches were found and which are most notable).

        Respond **only** with a valid JSON object in the following structure:

        {{
        "reply": "your helpful response here",
        "newOrder": [
            {{
            "name": "Branch Name",
            "address": "Branch Address",
            "operating_hours": "Operating hours string"
            }},
            ...
        ]
        }}

        ⚠️ Do not include any explanation, markdown, comments, extra keys, or partial data. Ensure every branch object includes all 3 required fields: `name`, `address`, and `operating_hours`.
        """

        print(prompt)

        response = requests.post(
            url=os.getenv("OPENROUTER_URL"),
            headers={
                "Authorization": f"Bearer {os.getenv("OPENROUTER_KEY")}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
                "messages": [{
                    "role": "user",
                    "content": [{ "type": "text", "text": prompt }]
                }],
                
            })
        )

        raw_content = response.json()["choices"][0]["message"]["content"]

        print(raw_content, "RAW")

        # Extract JSON block from markdown-style triple backticks
        json_str = re.search(r"```json\s*(\{.*\})\s*```", raw_content, re.DOTALL)
        if json_str:
            parsed_data = json.loads(json_str.group(1))
        else:
            # fallback if no code fence
            parsed_data = json.loads(raw_content)
        print(parsed_data, "PARSED")
        return {
            "status": "success", 
            "gemmaReply": parsed_data,
        }
    except Exception as e:
        print("error", e)
        return {"status": "error", "message": str(e)}
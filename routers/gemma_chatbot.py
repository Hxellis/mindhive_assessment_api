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

@router.post("/gemmaSendMsg")
def update_subway_branches(body: Message):
    try:            
        prompt = f"""
        You are a helpful assistant that helps users find Subway restaurant branches near them and answer relevant questions about Subway.

        User's current location: ({body.center['lat']}, {body.center['lng']})

        Here is a list of available Subway branches:
        {json.dumps(body.branches, indent=2)}

        User asked: "{body.question}"

        Your task:
        - Understand the user's question and determine the most relevant way to sort or filter the list of Subway branches.
        - If the question is about locations (e.g. "how many in Bangsar", "branches in Mont Kiara", "Subway near KLCC"), match using **fuzzy address or place name matching**.
        - Include branches that mention the place in their name OR are **commonly known to be within that area** even if not named exactly.
        - Use broader location context, not just exact string matches (e.g. KL Gateway Mall is in Bangsar South).
        - Return the **entire list of branches**, sorted appropriately in the `newOrder` field.
        - Include a helpful `reply` summarizing your answer (e.g. how many were found, and their names).

        Only respond in **pure JSON** with the following structure, do not include any additional explanation or formatting:
        {{ "reply": "your helpful response here", "newOrder": [/* entire branch list sorted appropriately */], }}

        Only respond with a valid JSON array of Subway branches in `newOrder`. Each item must contain `name`, `address`, and `operating_hours`. Do NOT include any dangling objects or partial entries. Do NOT include comments or additional formatting.
        """

        print(prompt)

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
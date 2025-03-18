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

@router.get("/updateSubway")
def update_subway_branches():
    try:
        count = findAndUpdateKLSubway()
        return {"status": "success", "updated_rows": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_table(subwayData):
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DBNAME")
    )
    cursor = db.cursor()

    cursor.executemany("""
        INSERT INTO subway_branches 
        (name, address, operating_hours, latitude, longtitude, waze_link)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            address = VALUES(address),
            operating_hours = VALUES(operating_hours),
            latitude = VALUES(latitude),
            longtitude = VALUES(longtitude),
            waze_link = VALUES(waze_link)
    """, subwayData)

    db.commit()
    cursor.close()
    db.close()

def findAndUpdateKLSubway():
    try:
        response = requests.get("https://www.subway.com.my/find-a-subway", headers={
            "User-Agent": "Mozilla/5.0"
        })
        html = response.text

        # Extract the JSON-like part using regex
        json_match = re.search(r'map\.init\((.*?)\);', html, re.DOTALL)

        if not json_match:
            raise ValueError("DATA NOT FOUND")

        json_data = json_match.group(1)  # Get matched JSON-like content

        # try:
        #     # Convert to a valid JSON object
        map_data = json.loads(json_data)

        subwayBranchList = map_data['markerData']

        subwayDataList = []
        for subway in subwayBranchList:
            html_content = subway['infoBox']['content']
            soup = BeautifulSoup(html_content, "html.parser")

            # Get name
            name = soup.find("h4").get_text(strip=True) if soup.find("h4") else ""

            # Get address (usually the first <p>)
            p_tags = soup.find_all("p")
            address = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else ""

            if "kuala lumpur" not in address.lower():
                continue  

            # Get hours (next <p> or nested ones)
            hours = []
            for p in p_tags[1:]:
                txt = p.get_text(strip=True)
                if txt and "Find out more" not in txt:
                    hours.append(txt)
            operating_hours = " | ".join(hours)

            # Get Waze link
            waze_link = ""
            for a in soup.find_all("a"):
                href = a.get("href")
                if href and "waze.com" in href:
                    waze_link = href
                    break

            # Get coordinates
            lat = subway["position"]["lat"]
            lng = subway["position"]["lng"]

            subwayDataList.append((
                name,
                address,
                operating_hours,
                float(lat),
                float(lng),
                waze_link
            ))

        update_table(subwayDataList)
        return len(subwayDataList)
            
    except Exception as e:
        print("Error: ", e)
        return 0

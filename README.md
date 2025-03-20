# Backend

A FastAPI server with a total of 3 endpoints ( +1 testing ) deployed on Render pulling data from a MySQL server deployed on freesqldatabase.com. Initial loading of site may be slow as both deployment services uses the free tier which will throttle after inactivity.

### How to locally run
<ol>
    <li>Clone and cd into the repo</li>
    <li>`pip install -r requirements.txt`</li>
    <li>`fastapi dev main.py`</li>
    <li>API should be accessible at http://localhost:8000 (default port), but enviromental files will still be needed</li>
</ol>


### Libraries (specified in requirements.txt)
FastAPI - API library\
uvicorn[standard] - Used for production deployment\
python-dotenv - Read enviromental files\
requests - Make http request, used in web scrapping Subway branches and chatbot messages\
pydantic - Comes with FastAPI, used to construct HTTP body structures when using POST\
mysql-connector-python - Connect to MySQL server and making queries\
beautifulsoup4 - Parsing webpage strings to scrape for data

### Endpoints

#### GET /test
Just returns a hello world, used to test

#### GET /getAllKLSubway
Gets all KL Subway branches available in the database and returns 

#### GET /updateSubway
Scrapes the "https://www.subway.com.my/find-a-subway" webpage for all Subway branches located in Kuala Lumpur, then proceeds to either `INSERT` or `UPDATE` the database depending if records already exist.

#### POST /chatbotSendMsg
Send a message with relavant data of of the user and the current filtered subway branches, and makes a HTTP request to a LLM (Google: Gemini Flash Lite 2.0 Preview) hosted on OpenRouter with a fixed prompt, allowing data to be parsed on the LLM's response and returned. Data consistency on questions may vvary due to it being a free model.

body={\
    center: object (lat: Num, lng: Num),\
    qustion: string,\
    branches: list [{ name: string, address: string, operating_hours: string }]\
}

### Enviromental Files
DB_HOST\
DB_USERNAME\
DB_PASSWORD\
DB_DBNAME\
OPENROUTER_URL\
OPENROUTER_KEY

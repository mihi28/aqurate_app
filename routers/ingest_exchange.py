import httpx
from fastapi import APIRouter, HTTPException

from config import EXCHANGE_RATES_URL
from database import exchange_rates_client

router = APIRouter(prefix="/ingest")


#helper function that converts the timestamp and date columns in the original json into strings
from dateutil import parser

def parse_date(val) -> str | None:
    try:
        return parser.parse(str(val)).isoformat()
    except ValueError:
        return None


#router endpoint
@router.post("/exchange_rates")
async def ingest_exchange():

    #connecting to the endpoint
    try:
        with httpx.AsyncClient() as client:
            response = client.get(EXCHANGE_RATES_URL)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException("Source endpoint returned {e.resonse.status_code}")

    except httpx.HTTPError as e:
        raise HTTPException("Could not reach endpoint")

    try:
        rows = response.json()
    except ValueError as e:
        raise ValueError("The endpoint did not return valid JSON")

    if not rows:
        return {"ingested": 0, "message": "Did not return any rows"}

    #creating the payload with data from the endpoint
    #list of dict with every column containing all the data, converted to the right type
    payload = []
    id = 1
    for row in rows:
        item = {}
        item["id"] = id
        item["date"] = parse_date(row.get("date"))
        item["base"] = str(row.get("base"))
        item["quote"] = str(row.get("quote"))
        item["rate"] = float(row.get("rate"))

        payload.append(item)
        id = id + 1
       

    #upserting the payload into the database
    try:
        result = (
            exchange_rates_client.table("exchange_rates").upsert(payload).execute()
        )
    except Exception as e:
        raise Exception("DATABASE UPSERT FAILED")

    return {"ingested": len(result.data), "message": "succesfully ingested the data from the endpoint"}
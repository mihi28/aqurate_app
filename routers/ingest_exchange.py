import httpx
from fastapi import APIRouter, HTTPException

from config import EXCHANGE_RATES_URL, SUPABASE_URL, SUPABASE_API_KEY
from database import get_client

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

    db = get_client().table("clean_orders")

    #fetching the earliest and latest date from the clean database
    earliestDate = db.select("fx_reference_date").order("fx_reference_date").limit(1).execute()
    latestDate = db.select("fx_reference_date").order("fx_reference_date",desc=True).limit(1).execute()

    #also fetching only the currencies used for transactions
    currencies = set()
    limit = 1000
    offset = 0
    while True:
        response = db.select("currency").neq("currency", "EUR").range(offset, offset + limit - 1).execute()
        batch = response.data

        if not batch:
            break

        for item in batch:
            currencies.add(item.get("currency"))

        if len(batch) < limit:
            break
        offset += limit
    quotes = ",".join(str(i) for i in currencies)
    print(quotes)
    #connecting to the endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXCHANGE_RATES_URL,
                                        params={"from":earliestDate,
                                                "to":latestDate,
                                                "quotes":quotes})
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
            get_client().table("exchange_rates").upsert(payload).execute()
        )
    except Exception as e:
        raise Exception("DATABASE UPSERT FAILED")

    return {"ingested": len(result.data), "message": "succesfully ingested the data from the endpoint"}
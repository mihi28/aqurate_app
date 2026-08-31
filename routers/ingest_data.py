import httpx
from fastapi import APIRouter, HTTPException

from config import RAW_SOURCE_URL,RAW_SOURCE_API
from database import raw_orders_client

router = APIRouter(prefix="/ingest")


#helper function that converts the timestamp and date columns in the original json into strings
from dateutil import parser

def parse_date(val) -> str | None:
    try:
        return parser.parse(str(val)).isoformat()
    except ValueError:
        return None


#router endpoint
@router.post("/orders_raw")
async def ingest_oders():

    #connecting to the endpoint
    try:
        with httpx.AsyncClient() as client:
            response = client.get(RAW_SOURCE_URL, RAW_SOURCE_API)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException("Source endpoint returned {e.resonse.status_code}: check the API key in .env")

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
    payload = [
        {
            "order_id":str(row.get("order_id")),
            "customer_id":int(row.get("customer_id")),
            "customer_email":str(row.get("customer_email")),
            "order_ts":parse_date(row.get("order_ts")),
            "status":str(row.get("status")),
            "channel":str(row.get("channel")),
            "sku":str(row.get("sku")),
            "product_name":str(row.get("product_name")),
            "category":str(row.get("category")),
            "qty":int(row.get("qty")),
            "unit_price":float(row.get("unit_price")),
            "currency":str(row.get("currency")),
            "country":str(row.get("country")),
            "fx_reference_date":parse_date(row.get("fx_reference_date"))
            }
            for row in rows
               ]

    #upserting the payload into the database
    try:
        result = (
            raw_orders_client.table("raw_orders_dest").upsert(payload).execute()
        )
    except Exception as e:
        raise Exception("DATABASE UPSERT FAILED")

    return {"ingested": len(result.data), "message": "succesfully ingested the data from the endpoint"}
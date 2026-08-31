import httpx
from fastapi import APIRouter, HTTPException
from datetime import datetime
from config import RAW_SOURCE_URL,RAW_SOURCE_API
from database import get_client

router = APIRouter(prefix="/ingest")


#helper function that converts the timestamp and date columns in the original json into strings
from dateutil import parser

def parse_date(val) -> str | None:
    if not val:
        return None
        
    val_str = str(val)
    
    #catch unix timestamps
    if val_str.isdigit():
        return datetime.fromtimestamp(int(val_str)).isoformat()
        
    # 2. Handle standard date formats with your existing parser
    try:
        return parser.parse(val_str).isoformat()
    except ValueError:
        return None


#router endpoint
@router.post("/orders_raw")
async def ingest_oders():

    #connecting to the endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(RAW_SOURCE_URL, 
                                        headers={ "apikey": RAW_SOURCE_API,
                                                 "Authorization": f"Bearer {RAW_SOURCE_API}"})
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
    payload = []

    id = 1
    for row in rows:
        item = {
        "id" : id,
        "order_id":str(row.get("order_id")),
        "customer_id":int(row.get("customer_id")) if row.get("customer_id") is not None else None,
        "customer_email":str(row.get("customer_email")) if row.get("customer_email") is not None else None,
        "order_ts":parse_date(row.get("order_ts")) if row.get("order_ts") is not None else None,
        "status":str(row.get("status")) if row.get("status") is not None else None,
        "channel":str(row.get("channel")) if row.get("channel") is not None else None,
        "sku":str(row.get("sku")) if row.get("sku") is not None else None,
        "product_name":str(row.get("product_name")) if row.get("product_name") is not None else None,
        "category":str(row.get("category")) if row.get("category") is not None else None,
        "qty":int(row.get("qty")) if row.get("qty") is not None else None,
        "unit_price":float(row.get("unit_price")) if row.get("unit_price") is not None else None,
        "currency":str(row.get("currency")) if row.get("customer_id") is not None else None,
        "country":str(row.get("country")) if row.get("customer_id") is not None else None,
        "fx_reference_date":parse_date(row.get("fx_reference_date")) if row.get("customer_id") is not None else None
        }
        payload.append(item)
        id = id+1

    #upserting the payload into the database
    try:
        result = (
            get_client().table("raw_orders_dest").upsert(payload).execute()
        )
    except Exception as e:
        raise Exception("DATABASE UPSERT FAILED")

    return {"ingested": len(result.data), "message": "succesfully ingested the data from the endpoint"}
import httpx
from fastapi import APIRouter, HTTPException

from config import SUPABASE_URL, SUPABASE_API_KEY
from database import get_client



router = APIRouter()

#router endpoint
@router.post("/clean_data")
async def clean_data():

    #connecting to the database
    rows = []
    limit = 1000
    offset = 0

    try:
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(f"{SUPABASE_URL}/rest/v1/raw_orders_dest", 
                                            headers={ "apikey": SUPABASE_API_KEY,
                                            "Authorization": f"Bearer {SUPABASE_API_KEY}"},
                                            params={
                                                "select": "*",
                                                "limit": limit,
                                                "offset": offset
                                            }
                                            )
                response.raise_for_status()

                try:
                    batch = response.json()
                    if not batch:
                        break

                    rows.extend(batch)

                    if len(batch) < limit:
                        break

                    offset += limit

                except ValueError as e:
                    raise ValueError("The endpoint did not return valid JSON")


    except httpx.HTTPStatusError as e:
        raise HTTPException("Source endpoint returned {e.resonse.status_code}")

    except httpx.HTTPError as e:
        raise HTTPException("Could not reach endpoint")

    if not rows:
        return {"ingested": 0, "message": "Did not return any rows"}

    #creating a payload containing all the cleaned data from the raw data table
    payload = []
    seen_items = set()
    id = 1
    for row in rows:

        #if category is null then we rename it into Unknown
        if row.get("category") is None:
            row["category"] = "Unknown"

        #removing all rows where customer_id is null
        if row.get("customer_id") is None:
            continue

        #removing rows where qty or price is 0 or negative
        if row.get("qty") < 0 or row.get("qty") == 0 or row.get("qty") is None:
            continue
        if row.get("unit_price") < 0 or row.get("unit_price") == 0 or row.get("unit_price") is None:
            continue

         #making sure all text fields are stripped from whitespaces
        #also making sure customer email, status, channel are lowercase
        row["customer_email"] = row.get("customer_email").strip().lower()
        row["status"] = row.get("status").strip().lower()
        row["channel"] = row.get("channel").strip().lower()
        row["order_id"] = row.get("order_id").strip()
        row["sku"] = row.get("sku").strip()
        row["product_name"] = row.get("product_name").strip()
        row["category"] = row.get("category").strip()
        row["currency"] = row.get("currency").strip()
        row["country"] = row.get("country").strip()

        #removing rows where status is test
        if row.get("status") == "test":
            continue

        #removing duplicate rows
        #i consider a duplicate row a row where the order_id and product name are the same
        #if multiple of the same item are within the same order, the quantity should be bigger instead of multiple instances of the same item
        item = (row.get("order_id"), row.get("product_name"))
        if item in seen_items:
            continue
        else:
            seen_items.add(item)
 
        payload.append(row)
       

    #upserting the payload into the database
    try:
        result = (
            get_client().table("clean_orders").upsert(payload).execute()
        )
    except Exception as e:
        raise Exception("DATABASE UPSERT FAILED")

    return {"total items inserted": len(result.data)}
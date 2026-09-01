from fastapi import APIRouter, HTTPException
from database import get_client

router = APIRouter()

@router.get("/country_breakdown")
async def get_country_breakdown():
    try:
        limit = 1000
        offset = 0
        rows = []
        while True:
            response = get_client().table("country_breakdown").select("*").range(offset, offset + limit - 1).execute()

            batch = response.data
            if batch is None:
                break

            rows.extend(batch)

            if len(batch) < limit:
                break

            offset += limit

        return {
            "status": "success",
            "total_countries": len(rows),
            "data": rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch country breakdown: {str(e)}")
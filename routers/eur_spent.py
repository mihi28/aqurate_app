from fastapi import APIRouter, HTTPException
from database import get_client

router = APIRouter()

@router.get("/customer-spend")
async def get_customer_spend():
    try:
        response = get_client().table("customer_spend_eur").select("*").execute()
        return {
            "status": "success",
            "total_customers": len(response.data),
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer spend: {str(e)}")
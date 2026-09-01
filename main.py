from fastapi import FastAPI

from routers import ingest_data, ingest_exchange, clean_data,country_breakdown, eur_spent, ingest_exchange

app = FastAPI()

#each task has an endpoint in a separate file in the routers folder

app.include_router(ingest_data.router)
app.include_router(ingest_exchange.router)
app.include_router(clean_data.router)
#app.include_router(country_breakdown.router)
app.include_router(eur_spent.router)


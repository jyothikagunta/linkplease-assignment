from fastapi import FastAPI
from routes.stats import router as stats_router
from app.database import Base, engine
from routes.rules import router as rules_router
from routes.webhook import router as webhook_router
from workers.dm_worker import start_worker


Base.metadata.create_all(bind=engine)


app = FastAPI(title="LinkPlease Assignment")


app.include_router(rules_router)
app.include_router(webhook_router)
app.include_router(stats_router)


@app.on_event("startup")
def startup():

    start_worker()


@app.get("/")
def root():

    return {
        "message": "LinkPlease API is running"
    }
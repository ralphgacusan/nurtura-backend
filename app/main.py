from fastapi import FastAPI
from app.core.database import engine
from sqlalchemy import text

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Nurtura backend running"}

@app.get("/db-test") # for database connection testing
async def db_test():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"database": "connected"}

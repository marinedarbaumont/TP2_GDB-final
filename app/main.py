from fastapi import FastAPI
from etl import etl

app = FastAPI(title="Graph Recs ETL")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/etl")
def run_etl():
    result = etl()
    return result
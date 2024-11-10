from fastapi import FastAPI, UploadFile, File, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import random
import csv
import io
import pandas as pd
from datetime import datetime, timedelta
import calendar
import glob
from fastapi.responses import StreamingResponse
from typing import List, Optional

app = FastAPI()

origins=[
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api/consent_count")
async def consent_count():
    Bank = 63
    TPAP = 25
    RSAS = 12
    return {
        'Bank' : Bank,
        'TPAP' : TPAP,
        'RSAS' : RSAS
    }

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
    allow_origins=origins,
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



class Merchant(BaseModel):
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    mcc_code: Optional[int] = None
    gst_no: Optional[str] = None
    tel_no: Optional[str] = None
    email: Optional[str] = None

# Define a list of merchants
merchants = [
    Merchant(
        merchant_name="QuickMart Superstore",
        merchant_id="QMRT123456",
        mcc_code=5411,
        gst_no="27ABCDE1234F1Z5",
        tel_no="+919876543210",
        email="support@hdfc.com"
    ),
    Merchant(
        merchant_name="FreshGrocer Market",
        merchant_id="FGMR789012",
        mcc_code=5411,
        gst_no="27ABCDE5678G1Z8",
        tel_no="+919812345678",
        email="info@freshgrocer.com"
    ),
    Merchant(
        merchant_name="TechZone Electronics",
        merchant_id="TZEL345678",
        mcc_code=5732,
        gst_no="27ABCDE9012H3Z9",
        tel_no="+919823456789",
        email="support@techzone.com"
    ),
    Merchant(
        merchant_name="HomeStyle Furniture",
        merchant_id="HSFR123987",
        mcc_code=5712,
        gst_no="27ABCDE3456K2Y6",
        tel_no="+919834567890",
        email="contact@homestyle.com"
    ),
    Merchant(
        merchant_name="BookNook Store",
        merchant_id="BNS123456",
        mcc_code=5942,
        gst_no="27ABCDE7890L4X3",
        tel_no="+919845678901",
        email="help@booknook.com"
    )
]


#get merchants
@app.get("/merchants", response_model=List[Merchant])
async def get_merchants():
    return merchants

#post merchants
@app.post("/merchants", response_model= Merchant, status_code=status.HTTP_201_CREATED)
async def create_merchant(merchant: Merchant):
    merchant.merchant_id = len(merchants) + 1
    merchants.append(merchant)
    return merchant
    
#delete merchant
@app.delete("/merchants/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_merchant(merchant_id : str):
    for merchant in merchants :
        if merchant.merchant_id == merchant_id:
            merchants.remove(merchant)
            return{"message" : "Merchant deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

#update merchant
@app.put("/merchants/{merchant_id}", response_model=Merchant)
async def update_merchant(merchant_id: str, merchant: Merchant):
    for i , existing_merchant in enumerate(merchants):
        if existing_merchant.merchant_id == merchant_id:
            merchants[i] = merchant
            return merchant
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")


#for user management

class User(BaseModel):
    user_id: Optional[int] = None  # Default value set to None for optional fields
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    company: Optional[str] = None
    date_added: str = datetime.now().strftime("%Y-%m-%d")  # This keeps the date in the format YYYY-MM-DD
    permissions: Optional[List[str]] = None  # Default is None instead of mutable default lis

users = [
    User(
        user_id =1 ,
        user_name = "Ravi",
        user_role = "Super Admin",
        company = "NPCI",
        date_added = "22-10-2023"
    ),
    User(
        user_id = 2 ,
        user_name = "Raman",
        user_role = "Admin",
        company = "HDFC",
        date_added = "22-10-2023"
    ),
]

#get users 
@app.get("/users", response_model=List[User])
async def get_users():
    return users
#create user
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    user.user_id = len(users) + 1  # auto-incrementing ID for simplicity
    users.append(user)
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user_role(user_id: int, new_role: str):
    for user in users:
        if user.user_id == user_id:
            user.user_role = new_role
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    global users
    users = [user for user in users if user.user_id!= user_id]
    return
    

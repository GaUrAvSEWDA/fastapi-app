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
    
# Initialize global DataFrames
df = pd.DataFrame()   # Placeholder for bank data
df2 = pd.DataFrame()  # Placeholder for TPAP data

# Function to load Excel file into DataFrame
def load_excel_file(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        if not df.empty:
            print("Data loaded successfully")
            return df
        else:
            print("Warning: The file is empty.")
            return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("Warning: The file is empty.")
        return pd.DataFrame()
    except UnicodeDecodeError:
        print("Error: Encoding issue with the file.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing the file: {e}")
        return pd.DataFrame()

# Load bank and TPAP data
file_path_bank = "./data/bank/data.xlsx"
file_path_tpap = "./data/TPAP/TPAP.xlsx"
df = load_excel_file(file_path_bank)
df2 = load_excel_file(file_path_tpap)

# Convert DataFrame to CSV
def dataframe_to_csv(df):
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

# Endpoint to download bank data as CSV
@app.get("/api/download_data_bank")
async def download_data_bank():
    if df.empty:
        raise HTTPException(status_code=404, detail="Bank data not available")
    csv_data = dataframe_to_csv(df)
    return StreamingResponse(csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=bank_data.csv"})

# Endpoint to download TPAP data as CSV
@app.get("/api/download_data_tpap")
async def download_data_tpap():
    if df2.empty:
        raise HTTPException(status_code=404, detail="TPAP data not available")
    csv_data = dataframe_to_csv(df2)
    return StreamingResponse(csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tpap_data.csv"})

# Endpoint to retrieve consent data for banks
@app.get("/consent_repository/bank")
async def get_consent_data():
    if df.empty:
        return {"error": "Data not available"}
    data = df.to_dict(orient="records")
    response = [
        {
            "Bank_Name": row["Bank_Name"],
            "total_Customers": row["total_Customers"],
            "total_Consents": row["total_Consents"],
            "withdraw_Consents": row["withdraw_Consents"]
        }
        for row in data
    ]
    return response

# Endpoint to retrieve TPAP consent data
@app.get("/consent_repository/tpap")
async def get_tpap_consent_data():
    if df2.empty:
        return {"error": "TPAP data not available"}
    tpap_data = df2.to_dict(orient="records")
    response = [
        {
            "TPAP_Name": row["TPAP_Name"],
            "total_Customers": row["total_Customers"],
            "total_Consents": row["total_Consents"],
            "withdraw_Consents": row["withdraw_Consents"]
        }
        for row in tpap_data
    ]
    return response

# Endpoint to upload and merge bank data
@app.post("/api/upload_data")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="File must be an Excel file")

    contents = await file.read()
    excel_df = pd.read_excel(io.BytesIO(contents))

    required_columns = {"Bank_Name", "total_Customers", "total_Consents", "withdraw_Consents"}
    if not required_columns.issubset(excel_df.columns):
        raise HTTPException(status_code=400, detail=f"Excel file must contain columns: {', '.join(required_columns)}")

    global df
    df = pd.concat([df, excel_df], ignore_index=True).drop_duplicates(subset=["Bank_Name"], keep="last")
    print("Updated DataFrame:", df)

    return {"status": "success", "message": "Data uploaded and merged successfully"}

# Endpoint to upload and merge TPAP data
@app.post("/api/upload_data_tpap")
async def upload_data_tpap(file: UploadFile = File(...)):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="File must be an Excel file")

    contents = await file.read()
    excel_df_tpap = pd.read_excel(io.BytesIO(contents))

    required_columns_tpap = {"TPAP_Name", "total_Customers", "total_Consents", "withdraw_Consents"}
    if not required_columns_tpap.issubset(excel_df_tpap.columns):
        raise HTTPException(
            status_code=400, 
            detail=f"Excel file must contain columns: {', '.join(required_columns_tpap)}"
        )

    global df2
    df2 = pd.concat([df2, excel_df_tpap], ignore_index=True).drop_duplicates(subset=["TPAP_Name"], keep="last")
    print("Updated TPAP DataFrame:", df2)

    return {"status": "success", "message": "TPAP data uploaded and merged successfully"}
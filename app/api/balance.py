import pandas as pd
from tempfile import NamedTemporaryFile
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas import balance as balance_schema
from app.models import models
from app.core.database import get_db

router = APIRouter()

@router.get("/balance/{user_id}", response_model=List[balance_schema.BalanceCreate])
def get_balance(user_id: int, db: Session = Depends(get_db)):
    """Get a user's balance by user ID."""
    balance = db.query(models.Balance).filter(models.Balance.user_id == user_id).all()
    return balance

@router.get("/balance/", response_model=List[balance_schema.BalanceCreate])
def get_all_balance(db: Session = Depends(get_db)):
    """Get overall balances for all users."""
    balance = db.query(models.Balance).order_by(models.Balance.id.asc()).all()  # Ordered by id ascending
    return balance

@router.get("/download", response_class=FileResponse)
def download_balance_sheet(db: Session = Depends(get_db)):
    balances = db.query(models.Balance).all()
    
    if not balances:
        raise HTTPException(status_code=404, detail="No balances found")

    # Create a temporary Excel file for the balance sheet using pandas
    df = pd.DataFrame([{
        'User ID': balance.user_id,
        'User Name': balance.user_name,
        'Amount Owed': balance.amount_owed,
    } for balance in balances])

    # Create a temporary Excel file
    with NamedTemporaryFile(delete=False, mode='wb') as temp_file:
        # Save the DataFrame to the Excel file
        df.to_excel(temp_file, index=False, engine='openpyxl')
        temp_file_path = temp_file.name

    # Serve the Excel file as a downloadable file
    return FileResponse(
        path=temp_file_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='balance_sheet.xlsx',
        headers={'Content-Disposition': 'attachment; filename=balance_sheet.xlsx'}
    )
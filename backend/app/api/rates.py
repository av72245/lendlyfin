"""
Rates API
- GET  /api/rates          — public, returns all active rates for frontend
- PUT  /api/rates/bulk     — admin/broker, bulk update all rates
- PATCH /api/rates/{id}    — admin/broker, update single rate
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Rate, User
from app.schemas.schemas import RateOut, RateUpdate, BulkRateUpdate, MessageResponse

router = APIRouter(prefix="/api/rates", tags=["rates"])


@router.get("", response_model=List[RateOut])
def get_rates(db: Session = Depends(get_db)):
    """
    Public endpoint — returns all active rates.
    The frontend calls this instead of reading from localStorage.
    """
    return db.query(Rate).filter(Rate.is_active == True).order_by(Rate.min_rate).all()


@router.put("/bulk", response_model=MessageResponse)
def bulk_update_rates(
    body:         BulkRateUpdate,
    db:           Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Broker/admin: update multiple rates at once.
    This is what the rates-admin.html page calls when 'Save All Rates' is clicked.
    """
    updated = 0
    for item in body.rates:
        bank_id = item.get("bank_id")
        if not bank_id:
            continue
        rate = db.query(Rate).filter(Rate.bank_id == bank_id).first()
        if not rate:
            continue
        if "min_rate" in item:    rate.min_rate    = float(item["min_rate"])
        if "max_rate" in item:    rate.max_rate    = float(item["max_rate"])
        if "comp_rate" in item:   rate.comp_rate   = float(item["comp_rate"])
        if "annual_fees" in item: rate.annual_fees = float(item["annual_fees"])
        rate.updated_at = datetime.utcnow()
        rate.updated_by = current_user.id
        updated += 1

    db.commit()
    return MessageResponse(message=f"{updated} rates updated successfully")


@router.patch("/{rate_id}", response_model=RateOut)
def update_rate(
    rate_id: int,
    body:    RateUpdate,
    db:      Session = Depends(get_db),
    _:       User = Depends(get_current_user),
):
    """Broker/admin: update a single rate by ID."""
    rate = db.query(Rate).filter(Rate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(rate, field, value)
    rate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rate)
    return rate

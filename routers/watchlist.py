from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.watchlist import Watchlist
from models.stock import StockCache
from models.user import User
from routers.auth import get_current_user

import yfinance as yf

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAdd(BaseModel):
    symbol: str


@router.get("/")
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    result = []
    for item in items:
        stock = db.query(StockCache).filter(StockCache.symbol == item.symbol).first()
        entry = {
            "symbol": item.symbol,
            "name":   stock.name   if stock else item.symbol,
            "sector": stock.sector if stock else "N/A",
            "close":  None, "change": None, "change_pct": None,
        }
        # Try to get live price — skip if fails
        try:
            t    = yf.Ticker(f"{item.symbol}.KA")
            hist = t.history(period="5d", interval="1d")
            if not hist.empty and len(hist) >= 2:
                c = float(hist["Close"].iloc[-1])
                p = float(hist["Close"].iloc[-2])
                entry["close"]      = round(c, 2)
                entry["change"]     = round(c - p, 2)
                entry["change_pct"] = round(((c - p) / p) * 100, 2) if p else 0
        except Exception:
            pass
        result.append(entry)
    return result


@router.post("/", status_code=201)
def add_to_watchlist(
    body: WatchlistAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symbol = body.symbol.upper().strip()
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol  == symbol,
    ).first()
    if existing:
        raise HTTPException(400, f"{symbol} already in watchlist")
    db.add(Watchlist(user_id=current_user.id, symbol=symbol))
    db.commit()
    return {"message": f"{symbol} added to watchlist"}


@router.delete("/{symbol}")
def remove_from_watchlist(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symbol = symbol.upper().strip()
    item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol  == symbol,
    ).first()
    if not item:
        raise HTTPException(404, f"{symbol} not in watchlist")
    db.delete(item)
    db.commit()
    return {"message": f"{symbol} removed"}


@router.get("/check/{symbol}")
def check_watchlist(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symbol = symbol.upper().strip()
    exists = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol  == symbol,
    ).first()
    return {"in_watchlist": exists is not None}
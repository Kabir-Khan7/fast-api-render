from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import Base, engine
from routers import auth, stocks, watchlist

app = FastAPI(title="PSX Analysis API")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://next-js-vercel-ashy.vercel.app/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://next-js-vercel-ashy.vercel.app/login"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    if engine:
        Base.metadata.create_all(bind=engine)
        # Seed stocks on first run
        try:
            from services.seed import seed_stocks
            from database import SessionLocal
            db = SessionLocal()
            seed_stocks(db)
            db.close()
        except Exception as e:
            print(f"Seed warning: {e}")

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)

@app.get("/")
def root():
    return {"status": "PSX Analysis API running"}
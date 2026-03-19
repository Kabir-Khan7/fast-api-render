import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import Base, engine
from routers import auth, stocks, watchlist

app = FastAPI(title="PSX Analysis API")

# Allow your Vercel frontend + local dev
ALLOWED_ORIGINS = [
    "https://next-js-vercel-ashy.vercel.app",
    "https://next-js-vercel-ashy.vercel.app/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup():
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
            from services.seed import seed_stocks
            from database import SessionLocal
            db = SessionLocal()
            seed_stocks(db)
            db.close()
        except Exception as e:
            print(f"Startup warning: {e}")

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)

@app.get("/")
@app.head("/")
def root():
    return JSONResponse({"status": "ok", "service": "PSX Analysis API"})
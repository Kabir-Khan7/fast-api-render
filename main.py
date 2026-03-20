import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="PSX Analysis API", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────────────
# IMPORTANT: Cannot use allow_origins=["*"] with allow_credentials=True
# Must list exact origins explicitly.
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://next-js-vercel-ashy.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "https://next-js-vercel-ashy.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
from routers import auth, stocks, watchlist

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)

# ── Startup: create tables + seed stocks ───────────────────────────────────
@app.on_event("startup")
async def startup():
    print("[startup] Starting PSX Analysis API...")
    try:
        from database import Base, engine, SessionLocal
        if engine is None:
            print("[startup] WARNING: No DATABASE_URL set — skipping DB setup")
            return

        Base.metadata.create_all(bind=engine)
        print("[startup] ✓ Tables ready")

        db = SessionLocal()
        try:
            from services.seed import seed_stocks
            n = seed_stocks(db)
            print(f"[startup] ✓ Seed done — {n} new stocks inserted")
        except Exception as e:
            print(f"[startup] Seed warning: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"[startup] ERROR: {e}")


# ── Health ─────────────────────────────────────────────────────────────────
@app.get("/")
@app.head("/")
def root():
    return JSONResponse({"status": "ok", "service": "PSX Analysis API"})


@app.get("/health")
def health():
    try:
        from database import SessionLocal
        from models.stock import StockCache
        db = SessionLocal()
        count = db.query(StockCache).count()
        db.close()
        return {"status": "healthy", "stocks_in_db": count}
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/admin/seed")
def force_seed():
    try:
        from database import SessionLocal
        from services.seed import seed_stocks
        db = SessionLocal()
        n = seed_stocks(db)
        db.close()
        return {"seeded": n}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
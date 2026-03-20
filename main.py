import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="PSX Analysis API", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────────────
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

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
    expose_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
from routers import auth, stocks, watchlist

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(watchlist.router)

# ── Startup ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    print("[startup] PSX Analysis API starting...")
    try:
        from database import Base, engine, SessionLocal
        if engine is None:
            print("[startup] WARNING: No database engine — DATABASE_URL missing")
            return

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("[startup] Tables created/verified")

        # Seed stocks
        db = SessionLocal()
        try:
            from services.seed import seed_stocks
            count = seed_stocks(db)
            print(f"[startup] Seed complete — {count} new stocks added")
        except Exception as e:
            print(f"[startup] Seed error: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"[startup] ERROR: {e}")


# ── Health endpoints ────────────────────────────────────────────────────────
@app.get("/")
@app.head("/")
def root():
    return JSONResponse({"status": "ok", "service": "PSX Analysis API", "version": "1.0.0"})


@app.get("/health")
def health():
    """Check DB connection and stock count."""
    try:
        from database import SessionLocal
        from models.stock import StockCache
        db = SessionLocal()
        count = db.query(StockCache).count()
        db.close()
        return {"status": "healthy", "stocks_in_db": count}
    except Exception as e:
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=500)


@app.post("/admin/seed")
def manual_seed():
    """Manually trigger stock seeding — call this once if /health shows 0 stocks."""
    try:
        from database import SessionLocal
        from services.seed import seed_stocks
        db = SessionLocal()
        count = seed_stocks(db)
        db.close()
        return {"message": f"Seeded {count} new stocks successfully"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
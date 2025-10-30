import os
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app

# -----------------------------------------------------------
# ✅ Create FastAPI and mount Flask
# -----------------------------------------------------------
app = FastAPI(title="AI Health Tracker")

def mount_flask():
    """Mount Flask inside FastAPI (at root '/')"""
    try:
        flask_app = create_app()
        app.mount("/", WSGIMiddleware(flask_app))
        print("✅ Flask dashboard mounted successfully at root '/'")
    except Exception as e:
        print(f"❌ Error mounting Flask app: {e}")

@app.on_event("startup")
def startup_event():
    mount_flask()
    print("🚀 FastAPI + Flask hybrid started")

# -----------------------------------------------------------
# ✅ Railway entrypoint
# -----------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("run:app", host="0.0.0.0", port=port)

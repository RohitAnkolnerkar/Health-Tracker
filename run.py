import os
from fastapi import FastAPI
from main import fastapi_app
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app

# -----------------------------------------------------------
# ✅ Mount Flask app at root ("/") or under "/flask"
# -----------------------------------------------------------

def mount_flask():
    """Mount Flask app inside FastAPI after startup."""
    try:
        flask_app = create_app()
        # Mount directly at root so your dashboard loads on /
        fastapi_app.mount("/", WSGIMiddleware(flask_app))
        print("✅ Flask app mounted successfully at root ('/').")
    except Exception as e:
        print(f"❌ Error mounting Flask app: {e}")

# -----------------------------------------------------------
# ✅ FastAPI startup event hook
# -----------------------------------------------------------

@fastapi_app.on_event("startup")
def startup_event():
    mount_flask()
    print("🚀 FastAPI + Flask hybrid app started successfully")

# -----------------------------------------------------------
# ✅ Railway entrypoint (FastAPI + Flask)
# -----------------------------------------------------------

app = fastapi_app  # Railway detects this automatically

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))  # Railway uses port 8080 by default
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=False)

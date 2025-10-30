import os
from fastapi import FastAPI
from main import fastapi_app
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app

# -----------------------------------------------------------
# ✅ Lazy-mount Flask app only once at startup
# -----------------------------------------------------------

def mount_flask():
    """Mount Flask app inside FastAPI after startup."""
    try:
        flask_app = create_app()
        fastapi_app.mount("/flask", WSGIMiddleware(flask_app))
        print("✅ Flask app mounted under /flask")
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
# ✅ Railway entrypoint
# -----------------------------------------------------------

app = fastapi_app  # Railway will look for variable named `app`

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=False)

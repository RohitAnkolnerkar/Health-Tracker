# run.py
import os
from fastapi import FastAPI
from main import fastapi_app

def mount_flask():
    """Mount Flask app inside FastAPI after startup (saves memory)."""
    from starlette.middleware.wsgi import WSGIMiddleware
    from app import create_app

    flask_app = create_app()
    fastapi_app.mount("/flask", WSGIMiddleware(flask_app))
    print("✅ Flask app mounted under /flask")

@fastapi_app.on_event("startup")
def startup_event():
    mount_flask()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)

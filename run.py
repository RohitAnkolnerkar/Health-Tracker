import os
from fastapi import FastAPI
from main import fastapi_app
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app

def mount_flask():
    try:
        flask_app = create_app()
        fastapi_app.mount("/", WSGIMiddleware(flask_app))
        print("✅ Flask app mounted successfully at root ('/').")
    except Exception as e:
        print(f"❌ Error mounting Flask app: {e}")

@fastapi_app.on_event("startup")
def startup_event():
    mount_flask()
    print("🚀 FastAPI + Flask hybrid app started successfully")

app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=False)

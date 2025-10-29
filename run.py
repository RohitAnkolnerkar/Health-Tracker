import os
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app

fastapi_app = FastAPI()

# Mount Flask app inside FastAPI
flask_app = create_app()
fastapi_app.mount("/", WSGIMiddleware(flask_app))  # mount at root

@fastapi_app.get("/status")
def status():
    return {"status": "✅ FastAPI is running on Render"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)

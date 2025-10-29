# run.py
import os
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from app import create_app
from main import fastapi_app

# Initialize Flask app
flask_app = create_app()

# Mount Flask app inside FastAPI
# Flask routes will be accessible under /flask/*
fastapi_app.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("run:fastapi_app", host="0.0.0.0", port=port, reload=False)

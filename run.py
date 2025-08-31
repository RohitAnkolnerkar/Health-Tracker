from app import create_app
import uvicorn
from multiprocessing import Process
from main import fastapi_app
from dotenv import load_dotenv
load_dotenv() 
def run_flask():
    app = create_app()
    # Listen on all interfaces inside Docker
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

def run_fastapi():
    # Listen on all interfaces inside Docker
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    flask_proc = Process(target=run_flask)
    fastapi_proc = Process(target=run_fastapi)

    flask_proc.start()
    fastapi_proc.start()

    try:
        flask_proc.join()
        fastapi_proc.join()
    except KeyboardInterrupt:
        print("Shutting down...")
        flask_proc.terminate()
        fastapi_proc.terminate()

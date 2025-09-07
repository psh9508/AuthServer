import uvicorn
import main_app
from src.routers.user import router as user_router

app = main_app.get_main_app()

app.include_router(user_router)

@app.get("/")
def fire():
    return 'Hello, World!'

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
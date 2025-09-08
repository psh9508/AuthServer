import uvicorn
import main_app
from src.routers.user import router as user_router
from src.routers.base import router as base_router

app = main_app.get_main_app()

app.include_router(user_router)
app.include_router(base_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
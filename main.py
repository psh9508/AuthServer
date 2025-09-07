import uvicorn
import main_app

app = main_app.get_main_app()

@app.get("/")
def fire():
    return 'Hello, World!'

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
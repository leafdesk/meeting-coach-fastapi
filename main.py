from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}


@app.get("/speech-to-text")
async def speech_to_text():
    return {"message": "speech-to-text"}

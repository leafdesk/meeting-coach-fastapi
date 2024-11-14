from fastapi import FastAPI

app = FastAPI()


@app.get("/fastapi")
async def root():
    return {"message": "Hello from FastAPI"}


@app.get("/fastapi/speech-to-text")
async def speech_to_text():
    return {"message": "speech-to-text"}

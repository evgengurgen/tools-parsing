from fastapi import FastAPI, UploadFile
from starlette.responses import JSONResponse

from backend.processor import processor

APP_VERSION: str = "1.0.0.0"

app = FastAPI()


@app.get("/")
async def health_check() -> JSONResponse:
    return JSONResponse({"message": "Ok", "version": APP_VERSION})


@app.post("/external_api/v1/parse/", status_code=200)
async def post_analitics_bd(
    file: UploadFile
) -> JSONResponse:
    await processor.check_file(file)

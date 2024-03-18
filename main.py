from fastapi import FastAPI, UploadFile
from starlette.responses import JSONResponse

from backend.processor import check_file

APP_VERSION: str = "1.0.0.0"

app = FastAPI()


@app.get("/")
async def health_check() -> JSONResponse:
    return JSONResponse({"message": "Ok", "version": APP_VERSION})


@app.post("/external_api/v1/anal/", status_code=200)
async def post_analitics_bd(
    file: UploadFile
) -> JSONResponse:
    await check_file(file)

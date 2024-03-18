from fastapi import UploadFile
from starlette.responses import JSONResponse


async def check_file(file: UploadFile) -> JSONResponse:
    return JSONResponse({"message": "Ok", "version": 1.0})

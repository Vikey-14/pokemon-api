from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler

app=FastAPI()

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):

    return JSONResponse (
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something unexpected went wrong on our side. Please try again later.",
            "details": str(exc)
        }
    )
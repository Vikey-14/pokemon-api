from fastapi import Request,FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

app=FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc: RequestValidationError):
    formatted_errors= [
        f"{".".join(str(loc) for loc in err["loc"][1:])}: {err["msg"]}"
        for err in exc.errors()
      ]
    
    return JSONResponse(

        status_code=422,
        content={
            "error": "Validation Failed.",
            "details": formatted_errors
        }
  )
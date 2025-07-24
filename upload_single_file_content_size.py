from fastapi import FastAPI,File,UploadFile
from fastapi.responses import JSONResponse

app=FastAPI()

@app.post("/upload/file", tags=["Admin Actions"], summary="Upload a single file", description="Accepts one uploaded file and returns its metadata")
async def file_upload(file: UploadFile= File(...)):
    content= await file.read()
    size=len(content)



    return JSONResponse(content= { "Filename": file.filename,
                                    "Content_type": file.content_type,
                                      "File_size_in_bytes": size
                                      })
from fastapi import FastAPI,File,UploadFile
from typing import List
from fastapi.responses import JSONResponse

app=FastAPI()

@app.post("/upload/size-check", tags=["Admin Actions"], summary="Upload files with size info", description="Returns size of each uploaded file and total bytes uploaded.")
async def upload_size_check(files: List[UploadFile] = File(...)):
    total_size = 0
    details = []

    for file in files:
        content = await file.read()
        size = len(content)
        total_size += size

        details.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size_bytes": size
        })

    return {
        "total_size_bytes": total_size,
        "file_details": details
    }

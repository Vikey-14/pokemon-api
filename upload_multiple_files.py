from fastapi import FastAPI, File, UploadFile
from typing import List
from fastapi.responses import JSONResponse

app=FastAPI()


@app.post("/upload/multiple/files", tags="Admin Actions", summary="Upload multiple files", description="Accepts multiple file uploads and returns info for each.")
async def mulitple_files(files: List[UploadFile]= File(...)):
    file_summaries=[]

    for file in files:
        content= await file.read()
        size=len(content)
        file_info={
            "Filename": file.filename,
            "Content Type": file.content_type,
            "File size bytes": size
        }
        file_summaries.append(file_info)


    return JSONResponse(content={"Uploaded Files": file_summaries})




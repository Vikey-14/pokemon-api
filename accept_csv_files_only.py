from fastapi import FastAPI,File,UploadFile
from typing import List
from fastapi.responses import JSONResponse

app=FastAPI()

@app.post("multiple/files/",tags=["Admin Actions"], summary="Upload CSV files only", description="Accepts multiple CSV files and rejects any non-CSV upload.")
async def upload_csv_only(files: List[UploadFile]= File(...)):
    accepted=[]
    rejected=[]

    for file in files:
        if file.content_type != "text/csv":
            rejected.append({"Filename": file.filename, "Reason": "Only CSV files allowed."})
            continue

        size= len(await file.read())
        accepted.append({"Filename":file.filename, "size": size})

        return JSONResponse(content={"Accepted": accepted, "Rejected": rejected})
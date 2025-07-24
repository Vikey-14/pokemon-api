from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/compare-upload")
async def compare_upload(
    file_bytes: bytes = File(...),
    file_stream: UploadFile = File(...)
):
    size_in_bytes = len(file_bytes)
    stream_name = file_stream.filename
    return {
        "Bytes Upload Size": size_in_bytes,
        "Streamed Filename": stream_name,
        "Stream Content Type": file_stream.content_type
    }

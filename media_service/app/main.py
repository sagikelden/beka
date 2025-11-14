from fastapi import FastAPI, File, UploadFile, HTTPException
import os, shutil, uuid
from pathlib import Path

app = FastAPI(title="Media Service")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    name = f"{uuid.uuid4().hex}{ext}"
    out_path = os.path.join(UPLOAD_DIR, name)
    try:
        with open(out_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"filename": name, "url": f"/uploads/{name}"}

@app.get("/uploads/{fname}")
async def serve(fname: str):
    path = os.path.join(UPLOAD_DIR, fname)
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return {"path": path, "note": "In production serve via CDN or nginx"}

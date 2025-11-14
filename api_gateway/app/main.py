from fastapi import FastAPI, Request, HTTPException
import httpx
import os

app = FastAPI(title="API Gateway")

AUTH_URL = os.getenv("AUTH_URL", "http://auth:8000")
LIVE_URL = os.getenv("LIVE_URL", "http://live:8000")
MEDIA_URL = os.getenv("MEDIA_URL", "http://media:8000")

@app.get("/")
async def root():
    return {"service": "api-gateway", "status": "ok"}

# Proxy to list matches
@app.get("/matches")
async def list_matches(q: str = None):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{LIVE_URL}/matches")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="live service error")
    return r.json()

# Proxy to subscribe to websocket — return endpoint info
@app.get("/ws-info")
async def ws_info():
    return {"ws_url": f"ws://{os.getenv('HOST', 'localhost')}:8000/ws"}  # info only

# User auth proxy (login)
@app.post("/login")
async def login(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{AUTH_URL}/login", json=body)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="API Gateway")

# Подключаем папки
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/health/db")
async def check_db():
    try:
        await db.command("ping")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}

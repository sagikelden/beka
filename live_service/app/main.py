from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import motor.motor_asyncio
import os, json
import redis.asyncio as aioredis
from app.models import Match
from bson import ObjectId
from typing import List

app = FastAPI(title="Live Scores Service")

MONGO = os.getenv("MONGO_URI", "mongodb://mongo:27017")
REDIS = os.getenv("REDIS_URI", "redis://redis:6379/0")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO)
db = client["otets_live_db"]

redis = None

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for conn in list(self.active):
            try:
                await conn.send_text(data)
            except:
                self.disconnect(conn)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    global redis
    redis = await aioredis.from_url(REDIS)
    # Start background listener
    async def reader():
        pubsub = redis.pubsub()
        await pubsub.subscribe("scores")
        async for message in pubsub.listen():
            if message and message.get('type') == 'message':
                try:
                    payload = json.loads(message.get('data'))
                    await manager.broadcast(payload)
                except Exception:
                    pass
    import asyncio
    asyncio.create_task(reader())

@app.get("/matches")
async def list_matches():
    docs = db.matches.find({})
    out = []
    async for d in docs:
        d['id'] = str(d['_id'])
        d.pop('_id', None)
        out.append(d)
    return out

@app.post("/matches")
async def create_match(match: Match):
    res = await db.matches.insert_one(match.dict(exclude_unset=True))
    return {"id": str(res.inserted_id)}

@app.post("/matches/{match_id}/score")
async def update_score(match_id: str, payload: dict):
    # update score in DB and publish to Redis
    m = await db.matches.find_one({"_id": ObjectId(match_id)})
    if not m:
        raise HTTPException(status_code=404, detail="Match not found")
    await db.matches.update_one({"_id": ObjectId(match_id)}, {"$set": {"score": payload.get("score"), "status": payload.get("status", m.get("status"))}})
    msg = {"match_id": match_id, "score": payload.get("score"), "status": payload.get("status", "live")}
    await redis.publish("scores", json.dumps(msg))
    return {"ok": True}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

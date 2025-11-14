from fastapi import FastAPI, HTTPException, Body
from passlib.context import CryptContext
import motor.motor_asyncio
import os
import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from app.schemas import UserCreate, UserOut 

app = FastAPI(title="Auth Service")

MONGO = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO)
db = client["otets_auth_db"]

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGO = "HS256"
ACCESS_EXPIRE_MINUTES = 60 * 24  # 1 день


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGO)


@app.post("/register")
async def register(user: UserCreate):
    users = db.users

    existing = await users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")


    password_safe_bytes = user.password.encode('utf-8')[:72]

    hashed = pwd_ctx.hash(password_safe_bytes)

    
    res = await users.insert_one({
        "email": user.email,
        "password": hashed,
        "name": user.name
    })

    return {"id": str(res.inserted_id), "email": user.email, "name": user.name}

@app.post("/login")
async def login(payload: dict = Body(...)):
    users = db.users
    u = await users.find_one({"email": payload.get("email")})
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    password_input = payload.get("password", "")

    password_safe_bytes = password_input.encode('utf-8')[:72]

    if not pwd_ctx.verify(password_safe_bytes, u["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": str(u["_id"]), "email": u["email"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/{user_id}", response_model=UserOut) 
async def get_user(user_id: str):
    users = db.users
    try:
        
        u = await users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
        
    return {"id": str(u["_id"]), "email": u["email"], "name": u.get("name")}

import os
import requests
import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# --- CONFIGURATION ---
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb+srv://saranclone:A@cluster0.xpustfk.mongodb.net/?appName=Cluster0")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "b5b3a09cb68c14296a3cc53b110096c4")
UPLOAD_API = os.getenv("UPLOAD_API", "https://api.imgbb.com/1/upload")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8887485449:AAE8xgLnpSa9G7P2bmD9P2qmIffZ-eVqNVM")

# Validation - Only warn, don't raise
if not MONGO_DB_URI:
    print("WARNING: MONGO_DB_URI not set, using default")
if not IMGBB_API_KEY:
    print("WARNING: IMGBB_API_KEY not set, using default")
if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN not set, using default")

app = FastAPI()

# Database Setup
client = AsyncIOMotorClient(MONGO_DB_URI)
db = client["JUST"]  # Database name

# --- HELPERS ---
async def validate_telegram_auth(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication header")
    
    init_data = authorization[4:]
    try:
        parsed_data = dict(parse_qsl(init_data))
        if "hash" not in parsed_data:
            raise ValueError("No hash in data")
            
        hash_value = parsed_data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        user_data = json.loads(parsed_data.get("user", "{}"))
        auth_user_id = user_data.get("id")
        
        if not auth_user_id:
            raise ValueError("User ID missing from initData")
            
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        is_valid = (calculated_hash == hash_value)
        
        if not is_valid:
            collection = db["clonebotdb"]
            user_bots = await collection.find({"user_id": auth_user_id}).to_list(length=100)
            
            for bot in user_bots:
                token = bot.get("token")
                if not token:
                    continue
                    
                bot_secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
                calc_hash = hmac.new(bot_secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
                
                if calc_hash == hash_value:
                    is_valid = True
                    break
                    
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid signature: Token mismatch")
            
        return auth_user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Authentication failed: {str(e)}")

def upload_to_imgbb(file_bytes) -> str:
    """Upload image bytes to ImgBB and return the public URL."""
    files = {"image": file_bytes}
    response = requests.post(
        UPLOAD_API,
        data={"key": IMGBB_API_KEY},
        files=files,
        timeout=60,
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data["data"]["url"]
    raise Exception(f"ImgBB upload failed: {response.text}")

# --- MODELS ---
class BotUpdate(BaseModel):
    bot_id: int
    user_id: int
    name: Optional[str] = None
    username: Optional[str] = None
    channel: Optional[str] = None
    support: Optional[str] = None
    start_img: Optional[str] = None
    ping_img: Optional[str] = None
    playlist_img: Optional[str] = None
    start_msg: Optional[str] = None
    logchannel: Optional[str] = None
    show_owner: Optional[bool] = None
    logging: Optional[bool] = None

# --- ROUTES ---

@app.get("/api/bots/{user_id}")
async def get_user_bots(user_id: int, auth_user_id: int = Depends(validate_telegram_auth)):
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access: UID mismatch")
    collection = db["clonebotdb"] 
    cursor = collection.find({"user_id": user_id})
    bots = await cursor.to_list(length=100)
    for bot in bots:
        bot["_id"] = str(bot["_id"])
    return bots

@app.post("/api/update_bot")
async def update_bot(update: BotUpdate, auth_user_id: int = Depends(validate_telegram_auth)):
    collection = db["clonebotdb"]
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    bot_id = update_data.pop("bot_id")
    user_id = update_data.pop("user_id")
    
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized attempt to modify different user's bot")
    
    result = await collection.update_one(
        {"bot_id": bot_id, "user_id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
    
    return {"status": "success", "message": "Bot updated successfully"}

@app.post("/api/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        url = upload_to_imgbb(contents)
        return {"status": "success", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files only if directory exists (use absolute path so this
# also works when the app is imported from api/index.py on Vercel, where the
# process cwd is not guaranteed to be the project root)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "Clone-Web API Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

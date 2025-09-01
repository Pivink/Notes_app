# server/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List
import secrets
from bson import ObjectId

from database import get_user_collection, get_note_collection, get_shared_link_collection
from models import UserCreate, UserLogin, NoteCreate, NoteUpdate, ShareRequest, Token
from auth import get_current_user, create_access_token, get_password_hash, verify_password

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)

@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    users_collection = get_user_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "password_hash": hashed_password,
        "name": user.name,
        "createdAt": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(result.inserted_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    users_collection = get_user_collection()
    
    # Find user
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

# Add the missing POST /notes endpoint
@app.post("/notes")
async def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    notes_collection = get_note_collection()
    
    note_data = {
        "ownerId": ObjectId(current_user["_id"]),
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "version": 1,
        "isDeleted": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await notes_collection.insert_one(note_data)
    return {"_id": str(result.inserted_id)}

@app.get("/notes")
async def get_notes(current_user: dict = Depends(get_current_user)):
    notes_collection = get_note_collection()
    
    # Use current_user["_id"] instead of current_user.id
    owner_id = ObjectId(current_user["_id"])
    
    notes = await notes_collection.find({
        "ownerId": owner_id,
        "isDeleted": False
    }).to_list(100)
    
    for note in notes:
        note["_id"] = str(note["_id"])
        note["ownerId"] = str(note["ownerId"])
    
    return notes

@app.get("/notes/{note_id}")
async def get_note(note_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    notes_collection = get_note_collection()
    note = await notes_collection.find_one({
        "_id": ObjectId(note_id),
        "ownerId": ObjectId(current_user["_id"]),  # Fixed: use ["_id"] instead of .id
        "isDeleted": False
    })
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["_id"] = str(note["_id"])
    note["ownerId"] = str(note["ownerId"])
    return note

@app.put("/notes/{note_id}")
async def update_note(note_id: str, note_update: NoteUpdate, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    notes_collection = get_note_collection()
    
    # Check if note exists and belongs to user
    note = await notes_collection.find_one({
        "_id": ObjectId(note_id),
        "ownerId": ObjectId(current_user["_id"]),  # Fixed: use ["_id"] instead of .id
        "isDeleted": False
    })
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Prepare update data
    update_data = {"updatedAt": datetime.utcnow()}
    if note_update.title is not None:
        update_data["title"] = note_update.title
    if note_update.content is not None:
        update_data["content"] = note_update.content
    if note_update.tags is not None:
        update_data["tags"] = note_update.tags
    
    update_data["version"] = note["version"] + 1
    
    await notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": update_data}
    )
    
    return {"message": "Note updated successfully"}

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    notes_collection = get_note_collection()
    
    # Check if note exists and belongs to user
    note = await notes_collection.find_one({
        "_id": ObjectId(note_id),
        "ownerId": ObjectId(current_user["_id"]),  # Fixed: use ["_id"] instead of .id
        "isDeleted": False
    })
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"isDeleted": True, "updatedAt": datetime.utcnow()}}
    )
    
    return {"message": "Note deleted successfully"}

@app.post("/notes/{note_id}/share")
async def share_note(note_id: str, share_request: ShareRequest, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")
    
    notes_collection = get_note_collection()
    shared_links_collection = get_shared_link_collection()
    
    # Check if note exists and belongs to user
    note = await notes_collection.find_one({
        "_id": ObjectId(note_id),
        "ownerId": ObjectId(current_user["_id"]),  # Fixed: use ["_id"] instead of .id
        "isDeleted": False
    })
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Generate unique token
    token = secrets.token_urlsafe(16)
    
    # Create shared link
    shared_link_data = {
        "noteId": ObjectId(note_id),
        "token": token,
        "expiresAt": share_request.expiresAt,
        "createdAt": datetime.utcnow()
    }
    
    await shared_links_collection.insert_one(shared_link_data)
    
    share_url = f"http://localhost:3000/shared/{token}"
    return {"shareUrl": share_url}

@app.get("/shared/{token}")
async def get_shared_note(token: str):
    shared_links_collection = get_shared_link_collection()
    notes_collection = get_note_collection()
    
    # Find shared link
    shared_link = await shared_links_collection.find_one({
        "token": token,
        "$or": [
            {"expiresAt": {"$exists": False}},
            {"expiresAt": None},
            {"expiresAt": {"$gt": datetime.utcnow()}}
        ]
    })
    
    if not shared_link:
        raise HTTPException(status_code=404, detail="Shared link not found or expired")
    
    # Get the note
    note = await notes_collection.find_one({
        "_id": shared_link["noteId"],
        "isDeleted": False
    })
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["_id"] = str(note["_id"])
    note["ownerId"] = str(note["ownerId"])
    return note

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
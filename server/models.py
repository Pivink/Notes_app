from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    email: EmailStr
    password_hash: str
    name: str
    createdAt: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Note(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    ownerId: PyObjectId
    title: str
    content: str
    tags: List[str] = []
    version: int = 1
    isDeleted: bool = False
    createdAt: datetime
    updatedAt: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class SharedLink(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    noteId: PyObjectId
    token: str
    expiresAt: Optional[datetime] = None
    createdAt: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ShareRequest(BaseModel):
    expiresAt: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
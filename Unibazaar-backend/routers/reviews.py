from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json, os
from datetime import datetime

router = APIRouter()
REVIEWS_FILE = "reviews.json"

if not os.path.exists(REVIEWS_FILE):
    with open(REVIEWS_FILE, "w") as f:
        json.dump([], f)

class Review(BaseModel):
    name: str
    email: str
    comment: str
    date: str

@router.get("/reviews")
async def get_reviews():
    with open(REVIEWS_FILE, "r") as f:
        reviews = json.load(f)
    return JSONResponse(reviews)

@router.post("/reviews")
async def post_review(review: Review):
    with open(REVIEWS_FILE, "r") as f:
        reviews = json.load(f)
    reviews.insert(0, review.dict())  
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)
    return JSONResponse(review.dict())

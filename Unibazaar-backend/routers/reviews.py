# routers/reviews.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json, os
from datetime import datetime

router = APIRouter()
REVIEWS_FILE = "reviews.json"

# Ensure the file exists
if not os.path.exists(REVIEWS_FILE):
    with open(REVIEWS_FILE, "w") as f:
        json.dump([], f)

# Pydantic model for validation
class Review(BaseModel):
    name: str
    email: str
    comment: str
    date: str

# GET all reviews
@router.get("/reviews")
async def get_reviews():
    with open(REVIEWS_FILE, "r") as f:
        reviews = json.load(f)
    return JSONResponse(reviews)

# POST new review
@router.post("/reviews")
async def post_review(review: Review):
    with open(REVIEWS_FILE, "r") as f:
        reviews = json.load(f)
    reviews.insert(0, review.dict())  # Add new review at the top
    with open(REVIEWS_FILE, "w") as f:
        json.dump(reviews, f, indent=2)
    return JSONResponse(review.dict())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import agent, faculty_agent, reviews  # ✅ Add reviews import

app = FastAPI(title="UniBazaar Backend", version="1.0")

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # use "*" during dev if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router)          # 💬 Chat + voice agent
app.include_router(faculty_agent.router)  # 🎓 Faculty search agent
app.include_router(reviews.router)        # ⭐ Review section routes

@app.get("/")
def root():
    return {"message": "UniBazaar AI Agent API is running 🤖🚀"}
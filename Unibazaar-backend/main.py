from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import agent, faculty_agent, reviews 

app = FastAPI(title="UniBazaar Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://unibazaar-kappa.vercel.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router)         
app.include_router(faculty_agent.router)  
app.include_router(reviews.router)       

@app.get("/")
def root():
    return {"message": "UniBazaar AI Agent API is running 🤖🚀"}
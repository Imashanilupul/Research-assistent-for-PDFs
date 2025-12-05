from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Research Management System Backend",
    description="Backend API for managing research projects, publications, and collaborations.",
    version="1.0.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Test msg": "Research Management System Backend is running!"}




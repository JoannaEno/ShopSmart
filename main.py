import asyncio
from functools import lru_cache
from apis.prisma import prisma
from apis.routes import router as apis
from fastapi import Depends, FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

async def startup_event():
    await prisma.connect()
    

async def shutdown_event():
   await prisma.disconnect()
    
origins = [
    "http://localhost:3000",
    "localhost:3000"
]


    
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(apis, prefix="/apis")
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

@app.get("/")
async def read_root():
    return {"Welcome to the API": "Please use " + settings.docs_url}

if __name__ == '__main__':
    asyncio.run(app.startup())
    
    
from concurrent.futures import ThreadPoolExecutor
from datasets import load_dataset
from openai import OpenAI
import numpy as np
import os
import sys
import threading
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import re
from fastapi import FastAPI
from routes.fetch import router as fetch_router
from routes.search import router as search_router
from contextlib import asynccontextmanager
from db import init_db, SessionLocal
from seed import seed
import asyncio


executor = ThreadPoolExecutor(max_workers=1)

def run_seed():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_seed)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(fetch_router)

app.include_router(search_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import subprocess
import asyncio
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def read_root():
    return {"message": "IPO Data API"}

@app.get("/api/ipos")
async def get_ipos():
    try:
        df = pd.read_csv('../ipo_data.csv')
        df = df.replace({np.nan: None})
        return df.to_dict('records')
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


@app.post("/api/refresh")
async def refresh_data():
    try:
        print("Starting refresh process...")

        # Get full paths
        python_path = "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"
        webscrape_path = os.path.join(BASE_DIR, 'webscrape.py')
        formatter_path = os.path.join(BASE_DIR, 'formatter.py')

        print(f"Running webscrape.py")
        # Run webscrape.py
        process1 = await asyncio.create_subprocess_exec(
            python_path, webscrape_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=BASE_DIR
        )
        stdout1, stderr1 = await process1.communicate()
        print(f"Webscrape output: {stdout1.decode()}")
        if stderr1:
            print(f"Webscrape error: {stderr1.decode()}")

        print("Running formatter.py")
        # Run formatter.py
        process2 = await asyncio.create_subprocess_exec(
            python_path, formatter_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=BASE_DIR
        )
        stdout2, stderr2 = await process2.communicate()
        print(f"Formatter output: {stdout2.decode()}")
        if stderr2:
            print(f"Formatter error: {stderr2.decode()}")

        return {"message": "Data refreshed successfully"}
    except Exception as e:
        print(f"Error during refresh: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
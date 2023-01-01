from fastapi import FastAPI
import uvicorn
import socket

from routers.message import message_router
from routers.user import user_router
from routers.status import status_router

app = FastAPI()

app.include_router(message_router)
app.include_router(user_router)
app.include_router(status_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    hostname=socket.gethostname()
    ip_address=socket.gethostbyname(hostname)
    print(f"Host Computer: {hostname} - {ip_address}")

    # run from terminal: uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
    uvicorn.run("__main__:app", host=ip_address, port=8000, reload=True)

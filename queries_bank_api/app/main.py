
from fastapi import FastAPI
from app.api.routes.v1.account_handlers import router as account_handler

app = FastAPI()
# Include routers
app.include_router(account_handler, prefix="/mybank/api/v1")

# ping route
@app.get("/")
async def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn
    print('Running queries bank api on port 8003')
    uvicorn.run(app, host="0.0.0.0", port=8003)

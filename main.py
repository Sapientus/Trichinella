import redis.asyncio as redis
from src.conf.config import settings
from fastapi import FastAPI
import uvicorn
from src.routes import contacts, auth, users
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from src.conf.config import settings

app = FastAPI()

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Initializes resources and performs setup tasks when the application starts up.

    This function is executed automatically when the FastAPI application starts up. It creates
    a connection to Redis using the provided settings, and initializes FastAPILimiter with the
    Redis connection.

    :return: None
    """
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    Handler for the root endpoint.
    This function is a handler for the root endpoint ("/"). It returns a JSON response containing
    a message.

    :return: A dictionary containing a message.
    """
    return {
        "message": "Did you know that in the reality everything is different than it actually is"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

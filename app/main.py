import logging
from fastapi import FastAPI

from app.routers.routes import router
from app.core.middlewares import setup_middlewares

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot API",
)

setup_middlewares(app)
app.include_router(router)

import logging
from fastapi import FastAPI

from app.routers.routes import router
from app.core.middlewares import setup_middlewares

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

app = FastAPI(
    title="Chatbot API",
)

setup_middlewares(app)
app.include_router(router)

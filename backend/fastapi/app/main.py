from fastapi import FastAPI
from .config import get_settings
from .routers import health

settings = get_settings()

def create_app() -> FastAPI:
    app = FastAPI(title="SoulSense FastAPI (scaffold)")
    app.include_router(health.router)

    @app.on_event("startup")
    async def startup_event():
        app.state.settings = settings

    return app


app = create_app()

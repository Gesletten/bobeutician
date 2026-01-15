"""
Entrypoint for routers in FastAPI
"""
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import qa, products, ingredients, chat

# Load environment variables from .env file
load_dotenv()



def create_app() -> FastAPI:
    """
    Mount routers in FastAPI with CORS support for frontend integration
    """
    application = FastAPI(
        title="BoBeutician API",
        description="AI-powered skincare consultation API",
        version="1.0.0"
    )

    # Add CORS middleware for frontend integration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    application.include_router(qa.router, prefix="/api/qa", tags=["QA"])
    application.include_router(products.router, prefix="/api", tags=["Products"])
    application.include_router(ingredients.router, prefix="/api", tags=["Ingredients"])

    return application

app = create_app()

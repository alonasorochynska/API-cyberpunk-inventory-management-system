from fastapi import APIRouter, FastAPI

from inventory import models
from database import engine

from inventory import router as inventory_router
from users import router as users_router

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

app = FastAPI(
    title="Cyberpunk Inventory Management API",
    description="This system manages the items that players can acquire in the game.",
    version="1.0.0",
    contact={
        "name": "Alona",
        "email": "alona.sorochynska.job@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(users_router.router)
app.include_router(inventory_router.router)


@app.get("/", tags=["initial"])
def welcome_message():
    return {
        "message": "Welcome to the Cyberpunk Inventory Management System API!",
        "info": "Use this API to manage users, items, and inventory. Access token "
                "authentication is required for most operations.",
        "endpoints": {
            "register": "/register",
            "login": "/token",
            "get_current_user": "/users/me",
            "get_items": "/items/",
            "get_categories": "/categories/",
            "documentation": "/docs"
        },
        "note": "You can explore and test the API through the interactive documentation "
                "available at /docs."
    }

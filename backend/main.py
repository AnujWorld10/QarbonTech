from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)
from fastapi.staticfiles import StaticFiles
from routes.api import router as api_router
from src.common.json_read import properties
from src.endpoints.descriptions import tags_metadata

app = FastAPI(openapi_tags=tags_metadata,docs_url=None, redoc_url=None, title="MEF APIs")

static_path = Path(__file__).parent.absolute() / "static"

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " QarbonTech - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " QarbonTech - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

origins = [properties["origin"]["origin_1"], properties["origin"]["origin_2"]]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



app.include_router(api_router)

from fastapi import APIRouter, Response

from .response_headers import add_headers

router = APIRouter(
    prefix="/v1"
)

# API to check if application server is up and running or not.
@router.get('/health-check', tags=["Health Check"])
def health_check(response:Response):
    """API to check web server is up or down."""
    add_headers(response)
    return {"detail":{"message":"Server is up","statusCode": 200,"errorCode": None}}

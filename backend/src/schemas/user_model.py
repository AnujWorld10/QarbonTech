from pydantic import BaseModel, Field

class AuthModel(BaseModel):
    clientId: str = Field(min_length = 1)
    clientSecret: str = Field(min_length = 1)

    
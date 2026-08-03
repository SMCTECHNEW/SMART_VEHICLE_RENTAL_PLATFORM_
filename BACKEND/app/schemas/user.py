from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None = None
    role: str

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
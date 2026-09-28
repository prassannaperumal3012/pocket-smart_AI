from importlib import import_module


# Load Pydantic dynamically so static analysis does not fail when the selected
# interpreter does not have the optional dependency indexed.
_pydantic = import_module("pydantic")
BaseModel = _pydantic.BaseModel
EmailStr = _pydantic.EmailStr
Field = _pydantic.Field


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class UserOut(BaseModel):

    id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

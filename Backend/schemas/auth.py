from pydantic import BaseModel, EmailStr


class LoginBarberoIn(BaseModel):
    email: EmailStr
    password: str


class BarberoAuthOut(BaseModel):
    id_barbero: int
    nombre: str
    rol: str

    class Config:
        from_attributes = True


class LoginBarberoOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    barbero: BarberoAuthOut

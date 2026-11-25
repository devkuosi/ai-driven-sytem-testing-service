from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Demo Registration API")

# Temporary storage: cleared when the application restarts.
users = {}


class Registration(BaseModel):
    email: str = Field(min_length=1)
    age: int = Field(ge=18, strict=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", status_code=201)
def register_user(registration: Registration):
    if registration.email in users:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = {
        "id": str(uuid4()),
        "email": registration.email,
        "age": registration.age,
    }
    users[registration.email] = user
    return user

@app.get("/users")
def find_users(email: str):
    user = users.get(email)
    return {"items": [user] if user else []}

@app.delete("/test-support/users", status_code=204)
def delete_test_user(email: str):
    users.pop(email, None)
    return Response(status_code=204)
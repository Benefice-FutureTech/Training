from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session, select
from jose import JWTError, jwt
from typing import List, Optional
from app.db import engine
from app.models import User
from pydantic import BaseModel

SECRET_KEY = "my-very-secret-key"
ALGORITHM = "HS256"

# --- FastAPI and CORS ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Dev only! For prod, use frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB startup ---
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- Dependency for DB session ---
def get_session():
    with Session(engine) as session:
        yield session

# --- User Update Pydantic model ---
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

# --- CRUD Endpoints ---

# Create user
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Get all users
@app.get("/users/", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

# Get user by id
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user by id
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.password is not None:
        user.password = user_update.password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Delete user by id
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return None

# --- JWT Helper Functions ---

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Auth endpoints ---

@app.post("/token")
def login(user: User, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    return {"msg": f"Hello {payload['sub']}! This is a protected route."}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

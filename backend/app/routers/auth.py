from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from .. import models, database, schemas
from ..deps.roles import get_current_user
from ..deps.roles import get_db, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Register attempt for: {user.email}")
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            print("Email already registered")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        # Default role is citizen
        new_user = models.User(
            email=user.email,
            name=user.name,
            password_hash=hashed_password,
            role="citizen"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created: {new_user.user_id}")
        return new_user
    except Exception as e:
        print(f"Registration error: {e}")
        raise e

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Login attempt for: {form_data.username}")
    # print(f"Password provided: {form_data.password}") # Check if password is being received
    
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user:
        print("User not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    print(f"User found: {user.user_id}, Role: {user.role}")
    
    is_valid = verify_password(form_data.password, user.password_hash)
    print(f"Password verification result: {is_valid}")
    
    if not is_valid:
        print(f"Password mismatch for {form_data.username}")
        # Debug hash comparison if needed
        # print(f"Hash in DB: {user.password_hash}")
        # print(f"Hash calculated: {get_password_hash(form_data.password)}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

from passlib.context import CryptContext
from datetime import datetime,timedelta
from jose import JWTError,jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status

hash_pass=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashed_pass(password):
   return hash_pass.hash(password)   

def verify_password(plain_password, hashed_password):
    return hash_pass.verify(plain_password, hashed_password) 

#JWT implimantation

SECRET_KEY="amijetoma"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def create_jwt(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM) 
    return encoded_jwt

#authrization

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token:str=Depends(oauth2_scheme)):
   try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        email:str=payload.get("sub")
        role:str=payload.get("role")

        if not email:
            raise HTTPException(status_code=404,detail="user not found")
        
        return{
            "email":email,
            "role": role
        }
   except JWTError:
       raise HTTPException(status_code=404,detail="Token expire or wrong")
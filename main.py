#import all the modules
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


#create user model
class User(BaseModel):
    username: str
    company: str
    password: str
class Login(BaseModel):
    username: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None

#run the fastapi
app = FastAPI()
@app.get('/')
def index():
    return {'data':'Hello World'}
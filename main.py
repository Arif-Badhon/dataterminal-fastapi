#import all the modules
import uvicorn
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Depends, Request,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashing import Hash
from jwttoken import create_access_token
from oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

from Dashboards.ed import economic_dashboard
from Dashboards.bd import business_dashboard
from Dashboards.id import industry_dashboard

#Run FastApi
app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#create user model
class User(BaseModel):
    username: str
    company: str
    designation: str
    email: str
    password: str
class Login(BaseModel):
    username: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None

#Database Creation in MongoDB
mongodb_uri = 'mongodb+srv://Badhon:arf123bdh@dataterminal1.gc4xk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["DATATERMINAL_USER"]

#Routes
@app.get("/")
def index():
    return{'data': 'Hello World'}

@app.get("/dashboard")
def dashboard(current_user:User = Depends(get_current_user)):
    return {
        "routes": [
            {"method": "GET", "path": "/dashboard", "summary": "Landing"},
            {"method": "GET", "path": "/dashboard/status", "summary": "App status"},
            {"method": "GET", "path": "/dashboard/ed", "summary": "Sub-mounted Dash application"},
            {"method": "GET", "path": "/dashboard/bd", "summary": "Sub-mounted Dash application"},
            {"method": "GET", "path": "/dashboard/id", "summary": "Sub-mounted Dash application"},
        ]
    }

@app.get("/dashboard/status")
def get_status(current_user:User = Depends(get_current_user)):
    return {"status": "ok"}

@app.post('/register')
def create_user(request:User):
	hashed_pass = Hash.bcrypt(request.password)
	user_object = dict(request)
	user_object["password"] = hashed_pass
	user_id = db["User_type1"].insert_one(user_object)
	# print(user)
	return {"res":"created"}

@app.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
	user = db["User_type1"].find_one({"username":request.username})
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'No user found with this {request.username} username')
	if not Hash.verify(user["password"],request.password):
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Wrong Username or password')
	access_token = create_access_token(data={"sub": user["username"] })
	return {"access_token": access_token, "token_type": "bearer"}


dash_app1 = economic_dashboard(requests_pathname_prefix="/dashboard/ed/")
app.mount("/dashboard/ed", WSGIMiddleware(dash_app1.server))

dash_app2 = business_dashboard(requests_pathname_prefix="/dashboard/bd/")
app.mount("/dashboard/bd", WSGIMiddleware(dash_app2.server))

dash_app3 = industry_dashboard(requests_pathname_prefix="/dashboard/id/")
app.mount("/dashboard/id", WSGIMiddleware(dash_app3.server))

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
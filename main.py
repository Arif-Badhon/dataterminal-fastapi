#import all the modules
from fastapi import FastAPI

#run the fastapi
app = FastAPI()
@app.get('/')
def index():
    return {'data':'Hello World'}
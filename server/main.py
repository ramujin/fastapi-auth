''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
from fastapi import FastAPI, Request, Response    # The main FastAPI import and Request/Response objects
from pydantic import BaseModel                    # Used to define the model matching the DB Schema
from fastapi.responses import HTMLResponse        # Used for returning HTML responses (JSON is default)
from fastapi.templating import Jinja2Templates    # Used for generating HTML from templatized files
from fastapi.staticfiles import StaticFiles       # Used for making static resources available to server
import uvicorn                                    # Used for running the app directly through Python
import dbutils as db                              # Import helper module of database functions!
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sessiondb import SessionManager
# from sessiondict import SessionManager

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
app = FastAPI()                                   # Specify the "app" that will run the routing
views = Jinja2Templates(directory='views')        # Specify where the HTML files are located
static_files = StaticFiles(directory='public')    # Specify where the static files are located
app.mount('/public', static_files, name='public') # Mount the static files directory to /public

session_manager = SessionManager(db.db_config, secret_key=db.session_config['session_key'], expiry=3600)
# session_manager = SessionManager(secret_key=db.session_config['session_key'])

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# A function to authenticate users when trying to login or use protected routes
def authenticate_user(username:str, password:str) -> bool:
  return db.check_user_password(username, password)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Authentication routes (login, logout, and a protected route for testing)
@app.post("/login")
def login(username:str, password:str, request:Request, response:Response):
  session = session_manager.get_session(request)
  if len(session) > 0:
    return {"message": "Already logged in"}

  # Authenticate the user here
  if authenticate_user(username, password):
    # Store session data
    session_data = {"username": username, "logged_in": True}
    session_id = session_manager.create_session(response, session_data)
    return {"message": "Login successful", "session_id": session_id}
  else:
    return {"message": "Invalid username or password"}

@app.post("/logout")
def logout(request:Request, response:Response):
  # End session and delete cookie
  session_manager.end_session(request, response)
  return {"message": "Logout successful"}

@app.get("/protected")
def protected_route(request:Request):
  # Get session data
  session = session_manager.get_session(request)
  # Check if user is logged in
  if len(session) > 0 and session.get("logged_in"):
    return {"message": "Access granted"}
  else:
    return {"message": "Access denied"}

# GET /sessions
@app.get('/sessions')
def get_sessions(request:Request) -> dict:
  return session_manager.get_session(request)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Home route to load the main page in a templatized fashion
# GET /
@app.get('/', response_class=HTMLResponse)
def get_home(request:Request) -> HTMLResponse:
  return views.TemplateResponse('index.html', {'request':request, 'users':db.select_users()})

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define a User class that matches the SQL schema we defined for our users
class User(BaseModel):
  first_name: str
  last_name: str
  username: str
  password: str

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# RESTful User Routes

# GET /users
@app.get('/users')
def get_users() -> dict:
  users = db.select_users()
  keys = ['id', 'first_name', 'last_name', 'username']
  users = [dict(zip(keys, user)) for user in users]
  return {"users": users}

# GET /users/{user_id}
@app.get('/users/{user_id}')
def get_user(user_id:int) -> dict:
  user = db.select_users(user_id)
  if user:
    return {'id':user[0], 'first_name':user[1], 'last_name':user[2], 'username':user[3]}
  return {}

# POST /users
# Used to create a new user
@app.post("/users")
def post_user(user:User) -> dict:
  new_id = db.create_user(user.first_name, user.last_name, user.username, user.password)
  return get_user(new_id)

# PUT /users/{user_id}
@app.put('/users/{user_id}')
def put_user(user_id:int, user:User) -> dict:
  return {'success': db.update_user(user_id, user.first_name, user.last_name, user.username, user.password)}

# DELETE /users/{user_id}
@app.delete('/users/{user_id}')
def delete_user(user_id:int) -> dict:
  return {'success': db.delete_user(user_id)}

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# If running the server directly from Python as a module
if __name__ == "__main__":
  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
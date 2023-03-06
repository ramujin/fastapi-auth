''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import bcrypt
import mysql.connector as mysql
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials
from sessiondb import SessionManager
# from sessiondict import SessionManager

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
load_dotenv('./credentials.env')                 # Read in the environment variables for MySQL
db_config = {
  "host": os.environ['MYSQL_HOST'],
  "user": os.environ['MYSQL_USER'],
  "password": os.environ['MYSQL_PASSWORD'],
  "database": os.environ['MYSQL_DATABASE']
}
session_manager = SessionManager(db_config, secret_key="mysecretkey")
# session_manager = SessionManager(secret_key="mysecretkey")

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def authenticate_user(username:str, password:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = 'select password from users where username=%s'
  cursor.execute(query, (username,))
  result = cursor.fetchone()
  cursor.close()
  db.close()

  if result is not None:
    return bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))
  return False

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
app = FastAPI()
@app.post("/login")
def login(username:str, password:str, request:Request, response:Response):
  session = session_manager.get_session(request)
  if session is not None:
    return {"message": "Already logged in"}

  # Authenticate the user here
  if authenticate_user(username, password):
    # Store session data
    session_data = {"username": username, "logged_in": True}
    session_id = session_manager.create_session(response, session_data)
    return {"message": "Login successful", "session_id": session_id}
  else:
    return {"message": "Invalid username or password"}

@app.get("/protected")
def protected_route(request:Request):
  # Get session data
  session = session_manager.get_session(request)
  # Check if user is logged in
  if session and session.get("logged_in"):
    return {"message": "Access granted"}
  else:
    return JSONResponse(status_code=401, content={"message": "Access denied"})

@app.post("/logout")
def logout(request:Request, response:Response):
  # End session and delete cookie
  session_manager.end_session(request, response)
  return {"message": "Logout successful"}
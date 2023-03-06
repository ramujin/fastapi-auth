''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import secrets

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class SessionManager:
  def __init__(self, secret_key:str, expiry:int=30):
    self.sessions = {}
    self.secret_key = secret_key
    self.expiry = expiry

  def create_session(self, response:Response, session_data:dict) -> str:
    session_id = secrets.token_urlsafe(16)
    self.sessions[session_id] = session_data
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return session_id

  def get_session(self, request:Request) -> dict | None:
    session_id = request.cookies.get("session_id")
    if session_id is not None:
      return self.sessions.get(session_id)

  def end_session(self, request: Request, response: Response) -> None:
    session_id = request.cookies.get("session_id")
    if session_id is not None:
      self.sessions.pop(session_id, None)
      response.delete_cookie(key="session_id")

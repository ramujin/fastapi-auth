''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from fastapi import Request, Response
import secrets

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Sessions:
  def __init__(self, expiry:int=3600) -> None:
    self.sessions = {}
    self.expiry = expiry # TODO: this is not implemented for dictionary sessions yet. if it was, it would be a cache!

  def create_session(self, response:Response, session_data:dict) -> str:
    session_id = secrets.token_urlsafe(16)
    self.sessions[session_id] = session_data
    response.set_cookie(key="session_id", value=session_id)
    return session_id

  def get_session(self, request:Request) -> dict:
    session_id = request.cookies.get("session_id")
    if session_id is not None:
      return self.sessions.get(session_id, {})
    return {}

  def end_session(self, request: Request, response: Response) -> None:
    session_id = request.cookies.get("session_id")
    if session_id is not None:
      self.sessions.pop(session_id, {})
      response.delete_cookie(key="session_id")

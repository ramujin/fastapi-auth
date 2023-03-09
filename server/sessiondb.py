''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import mysql.connector as mysql
from fastapi import Request, Response
import secrets, json
from datetime import datetime, timezone

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Sessions:
  def __init__(self, db_config:dict, secret_key:str, expiry:int=3600) -> None:
    self.db = SessionStore(db_config, expiry)
    self.db_config = db_config
    self.secret_key = secret_key

  def create_session(self, response:Response, session_data:dict) -> str:
    session_id = secrets.token_urlsafe(16)
    self.db.create(session_id, session_data)
    response.set_cookie(key="session_id", value=session_id)
    return session_id

  def get_session(self, request:Request) -> dict:
    session_id = request.cookies.get("session_id")
    return self.db.read(session_id)

  def end_session(self, request:Request, response:Response) -> None:
    session_id = request.cookies.get("session_id")
    self.db.delete(session_id)
    response.delete_cookie(key="session_id")

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class SessionStore:
  def __init__(self, db_config:dict, expiry:int) -> None:
    self.db_config = db_config
    self.expiry = expiry

  def create(self, session_id:str, session_data:dict) -> None:
    db = mysql.connect(**self.db_config)
    cursor = db.cursor()

    query = "insert into sessions (session_id, session_data) values (%s, %s)"
    cursor.execute(query, (session_id, json.dumps(session_data)))
    db.commit()

    cursor.close()
    db.close()

  def read(self, session_id:str) -> dict:
    if session_id is None:
      return {}

    db = mysql.connect(**self.db_config)
    cursor = db.cursor()

    query = "select session_data, created_at from sessions where session_id = %s"
    cursor.execute(query, (session_id,))
    result = cursor.fetchone()

    cursor.close()
    db.close()

    if result is None:
      return {}

    # Invalidate the session if it has expired; expiry is in units of seconds
    session_data, created_at = result
    elapsed = (datetime.utcnow() - created_at).total_seconds()
    if elapsed > self.expiry:
      self.delete(session_id)
      return {}

    return json.loads(session_data)

  def delete(self, session_id:str) -> None:
    if session_id is not None:
      db = mysql.connect(**self.db_config)
      cursor = db.cursor()

      query = "delete from sessions where session_id = %s"
      cursor.execute(query, (session_id,))
      db.commit()

      cursor.close()
      db.close()

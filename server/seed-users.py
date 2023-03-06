''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import mysql.connector as mysql
import bcrypt
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Collection of users with plain-text passwords – BIG NONO! NEVER EVER DO THIS!!!
users = [
  {'first_name':'Zendaya', 'last_name':'',          'username': 'ZD123',   'password': 'abc123'},
  {'first_name':'Tom',     'last_name':'Holland',   'username': 'tommy',   'password': 'abc123'},
  {'first_name':'Tobey',   'last_name':'Maguire',   'username': 'tobes',   'password': 'abc123'},
  {'first_name':'Andrew',  'last_name':'Garfield',  'username': 'drewie',  'password': 'abc123'},
  {'first_name':'Rick',    'last_name':'Gessner',   'username': 'rickg',   'password': 'drowssap'},
  {'first_name':'Ramsin',  'last_name':'Khoshabeh', 'username': 'ramujin', 'password': 'password'}
]

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Connect to the database
load_dotenv('../credentials.env')
config = {
  'host': os.environ['MYSQL_HOST'],
  'user': os.environ['MYSQL_USER'],
  'password': os.environ['MYSQL_PASSWORD'],
  'database': os.environ['MYSQL_DATABASE']
}
db = mysql.connect(**config)
cursor = db.cursor()

# Generate a salt for extra security
pwd_salt = bcrypt.gensalt()

# Insert every user with a salted and hashed password
for user in users:
  pwd = bcrypt.hashpw(user['password'].encode('utf-8'), pwd_salt)
  query = 'insert into users (first_name, last_name, username, password) values (%s, %s, %s, %s)'
  values = (user['first_name'], user['last_name'], user['username'], pwd)
  cursor.execute(query, values)

# Commit the changes and close the connection
db.commit()
cursor.close()
db.close()

print('Users seeded.')

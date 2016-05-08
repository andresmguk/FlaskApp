# config.py -> app's configurations 

# imports
import os

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db' 
USERNAME = 'admin' 
PASSWORD = 'admin' 
CSRF_ENABLED = True 
SECRET_KEY = '\x01\xb4\x14\x06\x81\x03\xb2YJz\xd9\x1a\x02\xb0\xed\xda\xdf\xdd\x80T/;\x1c\x15'

# define the full path for te database 
DATABASE_PATH = os.path.join(basedir, DATABASE)

# database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH


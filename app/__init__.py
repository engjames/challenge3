import os
from flask import Flask, jsonify
import psycopg2
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from flask_cors import CORS


UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Initialize application
app = Flask(__name__)
CORS(app)
# Initialize Bcrypt
app.config['SECRET_KEY'] = '12345678'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)
Swagger(app)


if os.getenv('db') == 'heroku':
    conn = psycopg2.connect(database = "d2q6gssvm0bjnj",user="edsqjauzzqelnw", password="2f6a2ae7d655cdd784afc27a1afc49a2a555c458332537033bda700f25373e97",host="ec2-107-22-162-8.compute-1.amazonaws.com",port=5432)
else: 
     conn = psycopg2.connect(database= "testdb")


# Import the application views
from app.views.user_views import GetAuthUrls
from app.views.incident_views import GetIncidentUrls
from app.views.redflag_views import GetRedflagUrls
GetAuthUrls.fetch_urls(app)
GetIncidentUrls.fetch_urls(app)
GetRedflagUrls.fetch_urls(app)


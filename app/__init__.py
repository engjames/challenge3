import os
from flask import Flask, jsonify
import psycopg2
from flask_bcrypt import Bcrypt

# Initialize application
app = Flask(__name__)

# Initialize Bcrypt
app.config['SECRET_KEY'] = '12345678'
bcrypt = Bcrypt(app)

if os.getenv('db') == 'heroku':
    conn = psycopg2.connect(database = "testdb")
    
conn = psycopg2.connect(database = "testdb")




# Import the application views
from app.views.user_views import GetAuthUrls
from app.views.incident_views import GetIncidentUrls
from app.views.redflag_views import GetRedflagUrls
GetAuthUrls.fetch_urls(app)
GetIncidentUrls.fetch_urls(app)
GetRedflagUrls.fetch_urls(app)


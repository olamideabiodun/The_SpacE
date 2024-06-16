from flask import Flask
from config import configur

app = Flask(__name__)
app.config.from_object(configur)

from app import routes
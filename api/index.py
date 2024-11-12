from flask import Flask
from app import create_app

app = create_app()

# Vercel serverless handler
def handler(request):
    if request.method == "POST":
        return app(request.environ, start_response)
    elif request.method == "GET":
        return app(request.environ, start_response)
    else:
        return app(request.environ, start_response)

# WSGI handler
def start_response(status, headers):
    return None 
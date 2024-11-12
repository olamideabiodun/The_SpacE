from app import create_app

app = create_app()

# If you need User and Post, import them after app is created
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

if __name__ == "__main__":
    app.run() 
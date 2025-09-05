from flask import Flask
import os
from config import Config
from models import db, User
from flask_cors import CORS
from flask_login import LoginManager
from auth import auth_bp
from uploads import uploads_bp
from workspaces import workspaces_bp
from chat import chat_bp

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")

db.init_app(app)
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(workspaces_bp, url_prefix="/api/workspaces")
app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
app.register_blueprint(chat_bp, url_prefix="/api/chat")

with app.app_context():
    db.create_all()
    print("DB created")
    
if __name__=="__main__":
    app.run(debug=True)
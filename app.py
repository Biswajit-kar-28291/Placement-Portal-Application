from flask import Flask
from application.database import db
app=None


def create_app():
    app=Flask(__name__)
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placementportal.sqlite3'
    app.config["UPLOAD_FOLDER"] = "static/resumes"
    db.init_app(app)
    app.app_context().push()
    return app


app=create_app()
from application.controllers import *

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        admin=User.query.filter_by(username="Admin").first()
        if admin is None:
            admin=User(username="Admin", email="admin@ex.com", role="admin",password="123")
            db.session.add(admin)
            db.session.commit()
    app.run()
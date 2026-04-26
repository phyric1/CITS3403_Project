#Use the built-in hash function in Flask to protect passwords
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),index=True,unique=True,nullable=False)
    email=db.Column(db.String(128),index=True,unique=True,nullable=False)
    password_hash=db.Column(db.String(256),nullable=True)

    #Store the encrypted hash password
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    #Check if the password is correct or not
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
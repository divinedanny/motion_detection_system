
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, current_user, login_user,login_required,logout_user
# from flask import Flask

# app = Flask(__name__, template_folder='./templates')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)



# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), index=True, unique=True)
#     email = db.Column(db.String(150), unique = True, index = True)
#     password_hash = db.Column(db.String(150))
#     joined_at = db.Column(db.DateTime(), default = datetime.datetime.utcnow, index = True)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self,password):
#       return check_password_hash(self.password_hash,password)
#import all the necessary packages
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_migrate import Migrate
from flask_uploads import IMAGES
from flask_uploads import UploadSet




# Create your first `UploadSet`.
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)

UPLOAD_FOLDER = '/static/assets/img' 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) 
#initialise Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SECRET_KEY']='sqlite:///database'
#for image files 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#for user session
app.permanent_session_lifetime = timedelta(minutes=10)

#initialise SQLAlchemy with Flask
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

#define the BlogPost table
class BlogPost(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  subtitle = db.Column(db.String(50))
  author = db.Column(db.String(50))
  date_posted = db.Column(db.DateTime)
  content = db.Column(db.Text)

#define the Users table
class Users(db.Model,UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50))
  email = db.Column(db.String(50))
  password = db.Column(db.String(50))
  profile_pic = db.Column(db.String(), nullable=True)
  date_posted = db.Column(db.DateTime)
  #content = db.Column(db.Text)

#main app code starts here****************((*))
  
with app.app_context(): #put all the code inside the app context
  #the homepage
  @app.route('/')
  def index():
    posts = BlogPost.query.all()
    print(type(current_user.profile_pic))
    return render_template("index.html", posts=posts, current_user=current_user)
  #the post page
  @app.route('/post/<int:post_id>')
  def post(post_id):
    post = BlogPost.query.filter_by(id=post_id).one()
    date_posted = post.date_posted.strftime('%B, %d, %Y')
    return render_template("post.html", post=post, date_posted=date_posted)
  #the page for adding posts from the frontend  
  @app.route('/add')
  @login_required
  def add():
    return render_template("add.html")
  #handles the posts
  @app.route('/addpost', methods=['POST'])
  def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']
    
    post = BlogPost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())
    db.create_all()
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))
  #posts code ends*************((*))
  
  #user accounts starts************((*))
  @login_manager.user_loader
  def load_user(id):
    return Users.query.get(int(id))

  @app.route('/login', methods=['POST', 'GET'])
  def login():
    if current_user.is_authenticated:
      flash("you are already loged in", 'error')
      return redirect(url_for('index'))
    if request.method == 'POST':
      session.permanent = True
      email = request.form['email']
      password = request.form['password']
      username = request.form['username']
      user = Users.query.filter_by(email=email).first()
      if user:
        password_is_same =check_password_hash(user.password, password)
        if password_is_same:
          flash("loged in successfully", 'success')
          session["user"]=username
          login_user(user, remember=True)
          next_page = request.args.get('next')
          return redirect(url_for(next_page)) if next_page else redirect(url_for('index'))
        else:
          flash("The username or password is incorrect", 'error')
      else:
        flash("email does not exist", "error")
    return render_template('login.html')
    
    #user profile
  @app.route('/user', methods=['POST', 'GET'])
  @login_required
  def user():
    if request.method == "POST":#updating the profile details
      current_user.username = request.form['username']
      current_user.email = request.form['email']
      
      #set the pic name
      pic_filename = secure_filename(current_user.profile_pic)
      #set uuid for the pic
      pic_name = str(uuid.uuid1()) + '_' + pic_filename
      current_user.profile_pic = pic_name #add the pic name to the database
      db.session.commit()
      flash("your profile has been updated successfully", "success")
      return redirect(url_for('user'))
    if 'user' in session:
      user_session = session["user"]
      user = Users.query.filter_by(username=current_user.username).first()
      print(user.username)
      return render_template("user.html",title="profile", user_session=user_session, current_user=current_user)
    else:
      return redirect(url_for('login'))
      
  @app.route('/signup', methods=['POST', 'GET'])
  def signup():
    if current_user.is_authenticated:
      flash("you are already signed up", 'error')
      return redirect(url_for('index'))
    if request.method == 'POST':
      username = request.form['username']
      email = request.form['email']
      password1 = request.form['password1']
      password2 = request.form['password2']
      profile_pic = request.files['profile_pic']
      
      email_exists = Users.query.filter_by(email=email).first()
      username_exists = Users.query.filter_by(username=username).first()
      if email_exists:
        flash('email already exists', 'error')
      elif username_exists:
        flash('username already exists', 'error')
      elif password1 != password2:
        flash("the passwords you entered do not match", 'error')
      elif len(password1) <7:
        flash("password is too short", 'error')
      elif len(username) <2:
        flash("username is too short", 'error')
      elif len(email) <10:
        flash("the email entered is invalid",'error')
      else:
        new_user = Users(username=username, email=email, password=generate_password_hash(password1, method='sha256'), profile_pic=profile_pic)
        db.create_all()
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('user created successfully','success')
        return redirect(url_for('index'))
    return render_template('signup.html')
    #logout
  @app.route('/logout')
  @login_required
  def logout():
    logout_user()
    session.pop("user", None)
    return redirect(url_for('index'))
  
  #run the Flask app
  if __name__ == "__main__":
    app.run(debug=True)

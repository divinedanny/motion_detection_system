# import beepy
import datetime
import os
import sys
import time
from threading import Thread
# from flask_modals import Modal
import cv2 as cv
import numpy as np
from flask import Flask, Response, flash, redirect, render_template, request,url_for,send_file
from flask_login import LoginManager, UserMixin, current_user, login_user,login_required,logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from io import BytesIO
from forms import LoginForm, RegistrationForm

detect=False
alarm = False
alarm_mode = False
alarm_counter = 0
camera = cv.VideoCapture(0)
camera_count= True
login_in=False

camera.set(cv.CAP_PROP_FRAME_WIDTH, 1040)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 780)

image_path = 'cerisedoucede-3.jpg'
protext_path = 'models/MobileNetSSD_deploy.prototxt'
model_path = 'models/MobileNetSSD_deploy.caffemodel'
min_confidence = 0.2


classes = ["backgroound", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "dorse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]



np.random.seed(876543210)
colors = np.random.uniform(0,255, size=(len(classes), 3))

net = cv.dnn.readNetFromCaffe(protext_path, model_path)

_, start_frame = camera.read()
start_frame = cv.cvtColor(start_frame, cv.COLOR_BGR2GRAY)
start_frame = cv.GaussianBlur(start_frame, (21, 21), 0)


alarm = False
alarm_mode = False
alarm_counter = 0
counter=1
capture=0


app = Flask(__name__, template_folder='./templates')


# day_time = input("is it morning: ")

# if day_time == "yes":
#     sensitivity = 20000000
# else:
#     sensitivity = 2000000
# if not os.path.exists('data'):
#         os.makedirs('data')



def beep_alarm():
    global alarm,counter
    time.sleep(2)
    for _ in range(10):
        if not alarm_mode:
            break
        print(f'ALARM {counter}')
        file = 'beep-04.mp3'
        os.system("afplay "+file)
        name = './data/frame' + str(counter) + '.jpg'
        print('Creating...' + name)
        # writing the extracted images
        cv.imwrite(name, frame_bw)
        counter+=1       
        
    #     file = request.files[name]
    #     upload = Upload(filename=file.filename, data=file.read())
    #     db.session.add(upload)
    #     db.session.commit()
                
    # print(f"Upload {name} succesfully")
    alarm = False
    
    
def detect_movement():
    global alarm,alarm_counter,alarm_mode,camera,start_frame,threshold,frame_bw,counter

    while True:
        _,frame = camera.read()
        height, width = frame.shape[0], frame.shape[1]
        blob = cv.dnn.blobFromImage(cv.resize(frame, (300, 300)), 0.007, (300,300), 130)

        net.setInput(blob)
        detected_object = net.forward()
        
        for i in range(detected_object.shape[2]):
    
            confidence = detected_object[0][0][i][2]

            if confidence> min_confidence:

                class_index = int(detected_object[0, 0, i, 1])

                upper_left_x = int(detected_object[0, 0, i, 3] * width)
                upper_left_y = int(detected_object[0, 0, i, 4] * height)
                lower_right_x = int(detected_object[0, 0, i, 5] * width)
                lower_right_y = int(detected_object[0, 0, i, 6] * height)

                prediction_text = f"{classes[class_index]}: {confidence: .2f}%"
                cv.rectangle(frame, (upper_left_x, upper_left_y), (lower_right_x, lower_right_y), colors[class_index], 3)
                cv.putText(frame, prediction_text, (upper_left_x, upper_left_y-15 if upper_left_y>30 else upper_left_y+15), cv.FONT_HERSHEY_SIMPLEX, 0.6, colors[class_index], 2)
        
        
        cv.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (30, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        if alarm_mode:
            frame_bw = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
            frame_bw = cv.GaussianBlur(frame_bw,(5,5), 0)
                
            difference = cv.absdiff(frame_bw,start_frame)
            threshold = cv.threshold(difference,25,255, cv.THRESH_BINARY)[1]
            start_frame=frame_bw
                            
            # if threshold.sum() > sensitivity:
            if threshold.sum() > 10000000:
                alarm_counter +=1
            else:
                if alarm_counter>0:
                    alarm_counter-=1
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            cv.imshow("Motion", frame)
                
        else:
            cv.VideoCapture(0)
                        
        if alarm_counter>20:
            if not alarm:
                alarm = True
                Thread(target=beep_alarm).start()  
                
        if (capture):
            name = './shot' + str(counter) + '.png'
            print('Creating...' + name)
            # writing the extracted images
            cv.imwrite(name, threshold)
            
        try:
            _, buffer = cv.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            pass
        else:
            pass
                    
                    
@app.route('/view_screanshots/<upload_id>')
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), as_attachment=True, attachment_filename=upload.filename)


def gen_frames():
    global alarm,alarm_counter,alarm_mode,camera,start_frame,threshold,frame_bw,detect
    while True:
        _,frame = camera.read()
        cv.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (30, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
       
        try:
            _, buffer = cv.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            pass
        else:
            pass
          
func = gen_frames()
               
@app.route('/')
def index():
    # if login_in == True:
    #     return redirect('index.html')
    return render_template("welcome.html")
    

@app.route('/video_feed')
# @login_required
def video_feed():
    return Response(func, mimetype='multipart/x-mixed-replace; boundary=frame')
   


@app.route('/requests', methods=['POST','GET'])
# @login_required
def tasks():
    global camera,func,alarm_mode,camera_count
    if request.method == 'POST':
        if request.form.get('nodetect') == 'No_Detect':
            global capture
            capture = 1
        elif request.form.get('stop') == 'Stop' and camera_count==False:
            camera_count=False
            camera.release()
            cv.destroyAllWindows()
        elif request.form.get('start') == 'Start' and camera_count==False:
            alarm_mode=False
            func = gen_frames()
        elif request.form.get('object') == "Detect":
            alarm_mode = True
            func = detect_movement()
            

            

    elif request.method == 'GET':
       
        return render_template('index.html')
    return render_template('index.html')
    


plain_password = "qwerty"
hashed_password = generate_password_hash(plain_password)
print(hashed_password)

hashed_password = generate_password_hash(plain_password)
submitted_password = "qwerty"
matching_password = check_password_hash(hashed_password,submitted_password)
print(matching_password)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


login_manager = LoginManager()
login_manager.init_app(app)



class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), index=True, unique=True)
  email = db.Column(db.String(150), unique = True, index = True)
  password_hash = db.Column(db.String(150))
  joined_at = db.Column(db.DateTime(timezone=True), default = datetime.datetime.utcnow, index = True)

  def set_password(self, password):
        self.password_hash = generate_password_hash(password)

  def check_password(self,password):
      return check_password_hash(self.password_hash,password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    
    



@app.route('/home')
def home():
    user = User.query.all()
    return render_template('index.html', user=user)

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username =form.username.data, email = form.email.data)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    global login_in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            # login_in = True
            return redirect(next or url_for('home'))
        flash('Invalid email address or Password.')    
    return render_template('login.html', form=form)



@app.route("/forbidden",methods=['GET', 'POST'])
@login_required
def protected():
    return redirect(url_for('forbidden.html'))

@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

cv.destroyAllWindows()

if __name__ == '__main__':
    app.run(debug=True)

import threading
import imutils
import cv2 as cv
import os
# import winsound

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1040)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 780)


_, start_frame = cap.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv.cvtColor(start_frame, cv.COLOR_BGR2HSV)
start_frame = cv.GaussianBlur(start_frame,(21,21),0)

alarm = False
alarm_mode = False
alarm_counter = 0

def beep_alarm():
    global alarm
    for _ in range(5):
        if not alarm_mode:
            break
        print(f'ALARM{alarm_counter}')
        file = 'beep-04.mp3'
        os.system("afplay "+file)
        # winsound.Beep(2500,1000)

    alarm = False
    
while True:
    _,frame = cap.read()
    frame = imutils.resize(frame, width=500)
    
    if alarm_mode:
        frame_bw=frame
        # frame_bw = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # frame_bw = cv.GaussianBlur(frame_bw,(5,5), 0)
        
        difference = cv.absdiff(frame_bw,start_frame)
        threshold = cv.threshold(difference,25,255, cv.THRESH_BINARY)[1]
        start_frame=frame_bw
        alarm_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        if threshold.sum() > 500000:
            alarm_counter +=1
        else:
            if alarm_counter>0:
                alarm_counter-=1
                
        cv.imshow("cam", alarm_frame)
        cv.imshow("cam", threshold)
        
    else:
        cv.imshow("cam",frame)
                
    if alarm_counter>20:
        if not alarm:
            alarm = True
            threading.Thread(target=beep_alarm).start()
            
    key_press = cv.waitKey(30)
    if key_press== ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    if key_press == ord("q"):
        alarm_mode = False
        break
    
cap.release()
cv.destroyAllWindows()
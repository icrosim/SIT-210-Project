import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
buzzer = 13
GPIO.setup(buzzer, GPIO.OUT)
LED = 15
GPIO.setup(LED, GPIO.OUT)
GPIO.output(buzzer, False)
GPIO.output(LED, False)

def SendMail(ImgFileName):
    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Intruder Detected'
    msg['From'] = 'abdulsamad6006@gmail.com'
    msg['To'] = 'asimarshad60@gmail.com'

    text = MIMEText("test")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('abdulsamad6006@gmail.com', 'samad6006')
    s.sendmail('abdulsamad6006@gmail.com', 'asimarshad60@gmail.com', msg.as_string())
    s.quit()


import sys
def Trackimages():
    now = time.time()  ###For calculate seconds of video
    future = now + 20
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("Trainner.yml")
    haarcascade = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(haarcascade)
    df =pd.read_csv("ResidentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    while True: 
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            print(conf)
            if (conf<75):
                aa = df.loc[df['Id']==Id]['Name'].values
                tt = str(Id)+"-"+aa
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 255), 7)
                cv2.putText(im,str(tt),(x+h,y),font,1,(0,25,255,),4)
            else:
                Id= 'Unknown'
                tt = str(Id)
                print(Id)
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                cv2.putText(im,str(tt),(x+h,y),font,1,(0,25,255),4)
                cv2.imwrite("UnknownPerson.jpg",im)
                SendMail("UnknownPerson.jpg")
                GPIO.output(LED, True)
                GPIO.output(buzzer, True)
                time.sleep(3)
                GPIO.output(LED, False)
                GPIO.output(buzzer, False)
                time.sleep(1)
        if time.time()>future:
            break
        cv2.imshow('Frame',im)
        key = cv2.waitKey(2) & 0xff
        if key == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
while True:
    i = GPIO.input(11)
    if i == 0:
        print("No motion detcted")
        sleep(0.3)
    elif i == 1:
        print("Motion detected")
        Trackimages()
        
 
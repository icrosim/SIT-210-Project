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

# #####Window is our Main frame of system
window = tk.Tk()
window.title("Facial Detection Security System")

window.geometry('1280x720')
window.configure(background='khaki')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except(TypeError, ValueError):
        pass
    return False


###For take images for datasets
def take_img():
    ID = IDtxt.get()
    name = Nametxt.get()
    if(is_number(ID)and name.isalpha()):
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            sampleNum = 0
            while (sampleNum<=100):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    # incrementing sample number
                    sampleNum = sampleNum + 1
                    # saving the captured face in the dataset folder
                    cv2.imwrite("TrainingImages\ " + name + "." + ID + '.' + str(sampleNum) + ".jpg", gray[y:y + h, x:x + w])
                    cv2.imshow('frame', img)
                # wait for 100 miliseconds
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
            cam.release()
            cv2.destroyAllWindows()
            res = "Images Saved for: "+ name
            ts = time.time()
            row = [ID, name]
            with open('ResidentDetails\ResidentDetails.csv', 'a+') as csvFile:
                writer = csv.writer(csvFile, delimiter=',')
                writer.writerow(row)
                csvFile.close()

            message2.configure(text = res)

###For train the model
def TrainImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces, Id = getImagesAndLabels("TrainingImages")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Images Trained. \nYou can now transfer to raspberry pi"
    message2.configure(text = res)

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faceSamples = []
    # create empty ID list
    Ids = []
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image

        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces = detector.detectMultiScale(imageNp)
        # If a face is there then append that in the list as well as Id of it
        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            Ids.append(Id)
    return faceSamples, Ids

window.grid_rowconfigure(0, weight=1) 
window.grid_columnconfigure(0, weight=1)

message = tk.Label(window, text="Facial Detection Security System", bg = "lavender", fg = "dark slate gray", width = 38,height=3,font=('Comic Sans',24))
message.place(x= 250, y=18)
message2 = tk.Label(window, text="", bg = "lavender", fg = "dark slate gray", width = 38,height=2,font=('Comic Sans',24))
message2.place(x= 250, y=550)
IDlabel = tk.Label(window, text="Enter ID", width=20, height=2, fg="black", bg="deepskyblue2", font=('Comic Sans', 15, ' bold '))
IDlabel.place(x=200, y=200)

def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True

IDtxt = tk.Entry(window, validate="key", width=20, bg="floral white", fg="red", font=('times', 25, ' bold '))
IDtxt['validatecommand'] = (IDtxt.register(testVal),'%P','%d')
IDtxt.place(x=550, y=210)

Namelabel = tk.Label(window, text="Enter Name", width=20, fg="black", bg="deepskyblue2", height=2, font=('Comic Sans', 15, ' bold '))
Namelabel.place(x=200, y=300)

Nametxt = tk.Entry(window, width=20, bg="floral white", fg="red", font=('times', 25, ' bold '))
Nametxt.place(x=550, y=310)

takeImg = tk.Button(window, text="Take Images",command=take_img,fg="black"  ,bg="Floral white"  ,width=20  ,height=3,font=('Comic Sans', 15, ' bold '))
takeImg.place(x=90, y=450)

trainImg = tk.Button(window, text="Train Images",command=TrainImages,fg="black"  ,bg="Floral white"  ,width=20  ,height=3,font=('Comic Sans', 15, ' bold '))
trainImg.place(x=550, y=450)

Quit = tk.Button(window, text="Quit",command=window.destroy,fg="black"  ,bg="Floral white"  ,width=20  ,height=3,font=('Comic Sans', 15, ' bold '))
Quit.place(x=990, y=450)
window.mainloop()
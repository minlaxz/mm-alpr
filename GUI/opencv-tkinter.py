import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import cv2


root = tk.Tk()
# Create a frame
app = Frame(root, bg="white")
app.grid()
# Create a label in the frame
lab = Label(app)
lab.grid()

# Capture from camera
cap = cv2.VideoCapture(0)

# function for video streaming
def video_stream():
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lab.imgtk = imgtk
    lab.configure(image=imgtk)
    lab.after(1, video_stream) 

video_stream()
root.mainloop()
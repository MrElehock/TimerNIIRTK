from tkinter import *
import math
import os
import time
import RPi.GPIO as GPIO
from threading import Thread
import serial
from PIL import Image
from PIL import Image, ImageTk
from glob import glob
import tkinter as tk

# GPIO Pins
KEY1 = 4
KEY2 = 20
KEY3 = 2
ENCODER_PIN_A = 17  # Replace pin
ENCODER_PIN_B = 18  # Replace pin
SWITCH_PIN = 27     # Encoder button

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY1, GPIO.OUT)
GPIO.setup(KEY2, GPIO.OUT)
GPIO.setup(KEY3, GPIO.OUT)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Constants
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#000000"
FONT_NAME = "Uroob"

class Arduino:
    def __init__(self,gui):
        self.is_value = True
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.gui = gui
    def read_potentiometer(self):
        num = 0
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        while self.is_value:
            if GPIO.input(KEY1) and self.is_value:
                num += 1
                print('Button pressed', num)
                time.sleep(0.2)
                if num == 2:
                    while num == 2:   
                        if (ser.inWaiting()> 0):
                            line123 = ser.readline().decode('utf-8').rstrip()
                            self.gui.update_title("Hours     ", RED)
                            if int(line123)<61:
                            	self.hours = int(line123)
                            	self.gui.update_timer_text(self.hours,self.minutes,self.seconds)
                            if GPIO.input(KEY1):
                                num = 3
                                time.sleep(1)
                if num == 3:                 
                    while num == 3:

                        if (ser.inWaiting()> 0):
                            line123 = ser.readline().decode('utf-8').rstrip()
                            self.gui.update_title("Minutes     ", RED)
                            if int(line123)<61:
                            	self.minutes = int(line123)
                            	self.gui.update_timer_text(self.hours,self.minutes,self.seconds)
                            if GPIO.input(KEY1):
                                num = 4
                                time.sleep(1)
                if num == 4:
                    while num == 4:

                        if (ser.inWaiting()> 0):
                            line123 = ser.readline().decode('utf-8').rstrip()
                            self.gui.update_title("Seconds     ", RED)
                            if int(line123) < 61:
                            	self.seconds = int(line123)
                            	self.gui.update_timer_text(self.hours,self.minutes,self.seconds)
                            if GPIO.input(KEY1):
                                num += 1
                if num >= 5:
                    ser.flush()
                    self.is_value = False
        return self.hours, self.minutes, self.seconds

class TimerClass:
    def __init__(self, arduino, gui):
        self.reps = 0
        self.remaining_time = 0
        self.is_paused = False
        self.arduino = arduino
        self.gui = gui

    def start_timer(self):
        self.arduino.read_potentiometer()
        curr_dir = os.path.dirname(__file__)
        '''image_files = glob(os.path.join(curr_dir, '*.jpg')) + glob(os.path.join(curr_dir, '*.png'))
        root = tk.Tk()
        root.title("dsafasdfasdf")
        if image_files:
        	image_path = image_files[0]
        	image = Image.open(image_path)
        	tk_image = ImageTk.PhotoImage(image)
        	label = tk.Label(root, image = tk_image)
        	label.pack()
        	root.mainloop()'''
    		
        count = self.arduino.hours * 3600 + self.arduino.minutes * 60 + self.arduino.seconds
        if self.remaining_time > 0:
            self.count_down(self.remaining_time)
            self.gui.update_title("Work       ", GREEN)
            self.remaining_time = count
        elif count > 0:
            self.count_down(count)
            self.gui.update_title("Work       ", GREEN)

    def count_down(self, count):
        if self.is_paused:
            self.remaining_time = count
            return

        count_hours = math.floor(count / 3600)
        count_min = math.floor((count % 3600) / 60)
        count_sec = count % 60
        self.gui.update_timer_text(count_hours, count_min, count_sec)

        if count > 0:
            self.gui.timer = self.gui.window.after(1000, self.count_down, count - 1)
        else:
            count+=1
            marks = ""
            work_sessions = math.floor(self.reps / 2)
            for _ in range(work_sessions):
                marks += "✔"
            self.gui.update_check_marks(marks)
        if GPIO.input(KEY2):
            self.pause_timer()
            time.sleep(0.1)

    def pause_timer(self):
        self.is_paused = not self.is_paused
        self.gui.update_title("Pause      ", GREEN)
        if self.is_paused:
            time.sleep(0.3)
        else:
        	time.sleep(0.3)
        	self.start_timer()
    def reset_timer(self):
        self.gui.window.after_cancel(self.gui.timer)
        self.gui.update_title("Timer      ", GREEN)
        self.gui.update_timer_text(0, 0, 0)
      
        self.reps = 0
        self.is_paused = False
        self.remaining_time = 0
        self.arduino.hours = 0
        self.arduino.minutes = 0
        self.arduino.seconds = 0
        self.arduino.is_value = True
        self.start_timer()

    def knopka_1(self):
        while True:
            if GPIO.input(KEY1):
                self.start_timer()
                time.sleep(0.4)
            if GPIO.input(KEY2):
                self.pause_timer()
                time.sleep(0.1)
            if GPIO.input(KEY3):
                self.reset_timer()
                time.sleep(0.1)

class TimerGUI:
    def __init__(self, timer_class):
    	
    	self.window = Tk()
    	self.window.title("TimerZen")
    	curr_dir = os.path.dirname(__file__)
    	image_path = os.path.join(curr_dir, "nii.png")
    	image = Image.open(image_path)
    	'''niiimg = PhotoImage(image)
    	self.canvas.create_image(0,0,niiimg)'''
    	
    	self.window.config(padx=100, pady=50, bg=YELLOW)
    	self.window.attributes('-fullscreen', True)
    	self.timer_class = timer_class
    	self.timer = None
    	
    	self.title_label = Label(text="Timer      ", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 100))
    	self.title_label.pack()
    	self.title_label.place(x = -100,y = 0)
    	self.title_label.grid(column=1, row=0)
    	
    	canvas_width = 1920
    	canvas_height = 1080
    	self.canvas = Canvas(self.window, width=canvas_width, height=canvas_height, bg=YELLOW, highlightthickness=0)
    	self.timer_text = self.canvas.create_text((canvas_width // 2) - 120, canvas_height // 2 + 20, text="00:00:00", fill="white", font=(FONT_NAME, 150, "bold"))
    	self.canvas.grid(column=1, row=1)
    	self.check_marks = Label(fg=GREEN, bg=YELLOW)
    	self.check_marks.grid(column=1, row=2)

    def update_title(self, text, color):
        self.title_label.config(text=text, fg=color)

    def update_timer_text(self, hours, minutes, seconds):
        self.canvas.itemconfig(self.timer_text, text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_check_marks(self, marks):
        self.check_marks.config(text=marks)

    def run(self):
        t1 = Thread(target=self.timer_class.knopka_1)
        t1.start()
        self.window.mainloop()

if __name__ == "__main__":
    timer_gui = TimerGUI(None)
    arduino = Arduino(timer_gui)

    timer_class = TimerClass(arduino, timer_gui)
    timer_gui.timer_class = timer_class
    timer_gui.run()


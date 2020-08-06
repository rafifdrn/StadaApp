#########################################################################
#### --------------- STADA USER INTERFACE SOFTWARE ------------------ ###
##########################################################################

#DESIGNED BY : RAFIF RAHMAN DARMAWAN
#LAST EDITED : 7/7/2020
#STATUS: IN PROGRESS


#----------------------LIBRARY-------------------------#

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sys
import time
import RPi.GPIO as GPIO
from hx711 import HX711
from picamera import PiCamera
from io import BytesIO
from pymongo import MongoClient
from pprint import pprint
import threading

# --- SET DPI AWARENESS FOR WINDOWS ONLY ---
try:
	from ctypes import windll
	windll.shcore.SetProcessDpiAwareness(1)
except:
	pass


# --- INITIALIZATION ---

referenceUnit = 360 #alter regarding weight sensor readings. 
pin_DT = 6 			#set the pins of load cell to Raspberry
pin_SCK = 5			#set the pins of load cell to Raspberry
minmass = 15		#minimum weight of mass to be captured
correctionval = 10 	#minimum value describing that the waste has been completely poured
finalval = [] 		#lists of values for correction
motorPin = 17		#set the pins of motor actuators
baseFreq = 50		#base frequency to operate the actuators
startpos = 2		#initial position of the motor
finalpos = 6		#final position of the motor

loggedin = False
onWeight = False
onCamera = False
onMotor = False


# ----------------- DESIGN PALETTE -------------------#

dark_gr = "#5e9a78"
light_gr = "#a7ce9f"
light_br = "#f7d98a"
dark_br = "#775934"
yellow = "#daa520"


# ------------------ CONTROLLER CLASS -----------------#

class Controller():
	def __init__(self):

		self.hx = HX711(pin_SCK,pin_DT) 

	def initialize(self):										# Calibrating the weight sensor and tare to zero as initial condition
		try:
			print("Initializing..")
			self.hx.set_reading_format("MSB", "MSB")
			self.hx.set_reference_unit(referenceUnit)
			self.hx.reset()
			self.hx.tare()

		except :
			print("There is a problem while initializing..")

		print("Calibration complete.")

	
	def measure_weight(self):									# Measures weight from a load and call handle_start()
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin_SCK, GPIO.IN)
		GPIO.setup(pin_DT, GPIO.OUT)

		global weight
		global loggedin
		global onWeight
		global onCamera

		if loggedin and onWeight:
			val = abs(round(self.hx.get_weight(5),2))
			if (val > minmass): 
				finalval.append(val)
				print (str(val) + " grams")
			else:
				print (str(val) + " grams")
				finalval.clear()
				
			if (len(finalval) >= 4):
				if (finalval[3] - finalval[0] < correctionval):
					weight = finalval[3]
					root.show_frame(PreviewFrame)
					self.handle_start()
					finalval.clear()
				else:
					finalval.clear()

	def handle_start(self):										# Handle capturing image by calling captureImage()

		global onWeight
		global onCamera
		global onMotor

		onWeight = False
		onCamera = True

		print ("Capturing..")
		try:
			self.captureImage()
			print("Image captured.")
		except:
			print("There is a problem while capturing")


	def captureImage(self):										# Capturing image

		global onCamera

		if onCamera:
			camera = PiCamera()
			camera.start_preview()
			time.sleep(3)
			camera.capture('/home/pi/Desktop/image.jpg')
			camera.stop_preview()
			camera.close()
			onCamera = False 

	def handle_send(self):										#Handle sending image captured to the server by calling sendImage() and called by the button "Confirm" in the Preview Frame
		try:
			self.sendImage()
			print("Image sent.")
		except:
			print("There is a problem while connecting to the server")
		root.show_frame(ConfirmationFrame)

	def sendImage(self):										#Sending image to the server
		pass


	def dump_waste(self):										#Handle moving actuators to dump the waste by calling moveServo() and called by the button "Correct" in the Confirmation Frame
		global onMotor
		onMotor = True

		root.show_frame(DashboardFrame)

		print("Dumping waste..")
		try:
			self.moveServo()
			onMotor = False
		except:
			print("There is a problem while moving the motor. Please contact our maintenance team!")
				
		print("Done!")

   

	def moveServo(self): 										#Moving the servo
		global onMotor
		global onWeight

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(motorPin, GPIO.OUT)
		servo = GPIO.PWM(motorPin, baseFreq)

		if onMotor:
			servo.start(0)
			time.sleep(1)
			servo.ChangeDutyCycle(finalpos)
			time.sleep(3)
			servo.ChangeDutyCycle(startpos)
			time.sleep(1)
			servo.stop()
			GPIO.cleanup()
			onMotor = False
			onWeight = True




# ------------------ USER CLASS -----------------------#
class User:
	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __str__(self):
		return f"User {self.username}."


user1 = User("rafif", "Wortel")



# --------------------- ROOT CLASS ----------------------#

class StadaAPP(tk.Tk):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.geometry("1368x768")
		self["background"] =  "White"

# --- STYLING ---

		style = ttk.Style()
		style.configure("Background.TFrame", background = light_gr)
		style.configure(
			"NormalLogo.TLabel",
			background = light_gr,
			)
		style.configure(
			"NormalText.TLabel",
			background = light_gr,
			font = ("Segoe UI", 14)
			)
		style.configure(
			"BigText.TLabel",
			foreground = dark_gr,
			font = ("Segoe UI", 48)
			)
		style.configure(
			"NormalText2.TLabel",
			font = ("Segoe UI", 14)
			)
		style.configure(
			"YesButton.TButton",
			background = dark_gr,
			font = ("Segoe UI Semibold", 14),
			foreground = "Black",
			)
		style.configure(
			"NoButton.TButton",
			font = ("Segoe UI SemiBold", 14),
			background = "red",
			foreground = "Black"
			)
		style.configure(
			"Normal.TCheckbutton",
    		background=light_gr,
    		)

# --- ROOT ---

		self.title("Stada : Smart Waste Management Software")
		self.columnconfigure(0, weight =1)
		self.rowconfigure(0, weight = 1)

		container = ttk.Frame(self)
		container.grid()
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.controller = Controller()

# --- WIDGETS ---
		
		self.frames = {}
		login_frame = LoginFrame(container, self, self.controller)
		dashboard_frame = DashboardFrame(container, self,self.controller)
		preview_frame = PreviewFrame(container, self, self.controller)
		confirmation_frame = ConfirmationFrame(container,self, self.controller)

# --- LAYOUTS ---
		dashboard_frame.grid(row = 0, column = 0, sticky = "NESW")
		login_frame.grid(row = 0, column = 0, sticky = "NESW")
		preview_frame.grid(row = 0, column = 0, sticky = "NESW")
		confirmation_frame.grid(row = 0, column = 0, sticky = "NESW")

# --- FRAMES TRANSITIONING ---

		self.frames[DashboardFrame] = dashboard_frame
		self.frames[LoginFrame] = login_frame
		self.frames[PreviewFrame] = preview_frame
		self.frames[ConfirmationFrame] = confirmation_frame


		# self.show_frame(ConfirmationFrame)					#UNCOMMENT DOI DAN COMMENT LINE BAWAHNYA UNTUK LIAT CONFIRMATION FRAME
		self.show_frame(LoginFrame)

		self.controller.initialize()							#Initializing weight sensor

	def show_frame(self, container):
		frame = self.frames[container]
		frame.tkraise()

	def authentication(self,*args):
		global loggedin
		global onWeight
		if (self.frames[LoginFrame].name_entry.get() == user1.username) and (self.frames[LoginFrame].password_entry.get() == user1.password):
			self.frames[LoginFrame].info_text.set("You are successfully logged in.")
			loggedin = True
			onWeight = True
			self.show_frame(DashboardFrame)

		else:
			self.frames[LoginFrame].info_text.set("Either username or password is incorrect.")

	def refresh_frame(self) :
		self.controller.measure_weight()

		image = Image.open('/home/pi/Desktop/image.jpg')
		imageres = image.resize((600, 450))
		self.frames[PreviewFrame].preview = ImageTk.PhotoImage(imageres)

		image_frame = ttk.Frame(self.frames[PreviewFrame])
		image_frame.grid(row = 1, column = 0)

		self.frames[PreviewFrame].photo_preview = ttk.Label(image_frame, image = self.frames[PreviewFrame].preview, padding = 20)
		self.frames[PreviewFrame].photo_preview.pack()
		self.after(500, self.refresh_frame)

# ------------------ FRAMES CLASS : LOGIN FRAME ----------------------#

class LoginFrame(ttk.Frame):
	def __init__(self, parent, app, controller):
		super().__init__(parent)

# --- VARIABLES ---
	
		self.controller = controller
		self.info_text = tk.StringVar()
		self.selected_option = tk.StringVar()
		self.image = Image.open("/home/pi/stadalogo.png")
		self.photo_logo = ImageTk.PhotoImage(self.image)

# --- WIDGETS ---
		
		self.logo = ttk.Label(self, image = self.photo_logo, padding = 5)
		self.name_label = ttk.Label(self, text = "Username: ")
		self.password_label = ttk.Label(self, text = "Password: ")
		self.name_entry = ttk.Entry(self, width = 25)
		self.password_entry = ttk.Entry(self, width = 25, show= "*")
		self.agree_checkbox = ttk.Checkbutton(self, width = 25, text = 'Agree to Terms and Conditions', variable = self.selected_option, command = self.enableButton)
		self.signIn_button = ttk.Button(self, text = "Login", state = "disabled", cursor = "hand2", command = lambda : app.authentication(DashboardFrame))
		self.info_label = ttk.Label(self, textvariable= self.info_text)

# --- LAYOUTS ---

		self.logo.grid(row = 0, column = 0, rowspan = 2, pady = (30), padx = (300,0))
		self.name_label.grid(row = 0, column = 1, sticky = 'WS', pady = 20)
		self.password_label.grid(row = 1, column = 1, sticky = 'WN')
		self.name_entry.grid(row = 0, column = 2, sticky = 'S', pady = 20, padx = (0, 300))
		self.password_entry.grid(row = 1, column = 2, sticky = 'N', padx = (0,300))
		self.agree_checkbox.grid(row = 2, column = 0, columnspan = 3, pady = 20)
		self.signIn_button.grid(row = 3, column = 0, columnspan = 3, pady = 30)
		self.info_label.grid(row = 4, column = 0, columnspan = 3, pady = 30)

# --- FUNCTIONS ---

	def enableButton(self, *args):
		if (int(self.selected_option.get()) == 1):
			self.signIn_button["state"] = "enabled"
		else:
			self.signIn_button["state"] = "disabled"


# ------------------ FRAMES CLASS : DASHBOARD FRAME ----------------------#

class DashboardFrame(ttk.Frame):
	def __init__(self, parent, app, controller):
		super().__init__(parent)

		self["style"] = "Background.TFrame"
		self.controller = controller
		self.grid_rowconfigure(0, weight= 0)
		self.grid_rowconfigure(1, weight = 10)
		self.grid_rowconfigure(2, weight = 10)
		self.grid_columnconfigure(0, weight = 1)

		title_frame = ttk.Frame(self, style = "Background.TFrame")
		title_frame.grid(row = 0, column = 0, sticky = "NSEW")

		main_frame = ttk.Frame(self, padding = 20)
		main_frame.grid(row = 1, column = 0, sticky = "NSEW")

		secondary_frame = ttk.Frame(self, padding = 20)
		secondary_frame.grid(row = 2, column = 0, sticky = "NSEW")
		secondary_frame.grid_columnconfigure(0, weight = 4)
		secondary_frame.grid_columnconfigure(1, weight = 1)
		secondary_frame.grid_rowconfigure(0, weight = 4)
		secondary_frame.grid_rowconfigure(1, weight = 1)

# --- VARIABLES ---

		image = Image.open("/home/pi/stadalogo.png")
		imageres = image.resize((120,120))
		self.photo_logo = ImageTk.PhotoImage(imageres)

# --- WIDGETS ---

		self.logo = ttk.Label(title_frame, image = self.photo_logo, style ="NormalLogo.TLabel" )
		self.greet_label = ttk.Label(title_frame, text ="My Dashboard", style = "NormalText.TLabel")
		self.totalwaste_label = ttk.Label(main_frame, text = "Total Waste in System :", style = "NormalText2.TLabel")
		self.sustainable_label = ttk.Label(secondary_frame, text = "Energy produced :", style = "NormalText2.TLabel")

# --- LAYOUTS ---

		self.logo.grid(row = 0, column =0, sticky = "E")
		self.greet_label.grid(row = 0, column = 1, sticky = "E")
		self.totalwaste_label.grid()
		self.sustainable_label.grid(row = 0, column = 0, sticky = 'NW')


# --- FUNCTIONS ---

# ------------------ FRAMES CLASS : PREVIEW FRAME ----------------------#

class PreviewFrame(ttk.Frame):
	def __init__(self, parent, app, controller):
		super().__init__(parent)

		self.grid_rowconfigure(0, weight= 1)
		self.grid_rowconfigure(1, weight = 5)
		self.grid_rowconfigure(2, weight = 3)
		self.grid_columnconfigure(0, weight = 1)

		image = Image.open('/home/pi/Desktop/image.jpg')
		imageres = image.resize((600, 450))
		self.preview = ImageTk.PhotoImage(imageres)

		title_frame = ttk.Frame(self, style = "Background.TFrame")
		title_frame.grid(row = 0, column = 0, sticky = "NSEW")

		image_frame = ttk.Frame(self)
		image_frame.grid(row = 1, column = 0)

		secondary_frame = ttk.Frame(self)
		secondary_frame.grid(row = 2, column = 0)


# --- WIDGETS ---

		titleLbl = ttk.Label(title_frame, text = "Preview", style = "NormalText.TLabel", padding = 20)
		self.photo_preview = ttk.Label(image_frame, image = self.preview, padding = 20)
		self.weightLbl = ttk.Label(secondary_frame, text = "Weight :", style = "NormalText2.TLabel")
		self.weightInfo = ttk.Label(secondary_frame, textvariable = "50 g")
		self.currentProcessLbl = ttk.Label(secondary_frame, text = "Current Process :", style = "NormalText2.TLabel")
		self.currentProcessInfo = ttk.Label(secondary_frame, textvariable = "Measuring...")
		self.Backbtn = ttk.Button(secondary_frame, text = "Confirm" , padding = 10, command = controller.handle_send)

# --- LAYOUTS ---

		titleLbl.grid(row = 0, column = 0, sticky = "NSEW")
		self.photo_preview.pack()
		self.weightLbl.grid(row =0, column = 0, padx = 100)
		self.weightInfo.grid(row = 0, column = 1, padx = 100)
		self.currentProcessLbl.grid(row =0, column = 2, padx = 100, pady = (0))
		self.currentProcessInfo.grid(row =0, column = 3, padx = 100, pady = (0))
		self.Backbtn.grid (row = 1, column = 0, columnspan = 4, padx = 200, pady = (20, 20))

# ------------------ FRAMES CLASS : CONFIRMATION FRAME ----------------------#

class ConfirmationFrame(ttk.Frame):
	def __init__(self, parent, app, controller):
		super().__init__(parent)

		self.grid_rowconfigure(0, weight = 0)
		self.grid_rowconfigure(1, weight = 8)
		self.grid_rowconfigure(2, weight = 0)
		self.grid_columnconfigure(0, weight = 1)

		image = Image.open("/home/pi/Desktop/image.jpg")
		imageres = image.resize((450, 300))
		self.preview = ImageTk.PhotoImage(imageres)

		title_frame = ttk.Frame(self, style = "Background.TFrame")
		title_frame.grid(row = 0, column = 0, sticky = "NSWE")

		main_frame = ttk.Frame(self)
		main_frame.grid(row = 1, column = 0 , sticky = "NSEW")

		button_container = ttk.Frame(self, style = "Background.TFrame")
		button_container.grid(row = 2, column = 0, sticky = "NSWE")

		main_frame.grid_columnconfigure(0, weight = 1)
		main_frame.grid_columnconfigure(1, weight = 3)

		image_frame =  ttk.Frame(main_frame, padding = 5)
		image_frame.grid(row = 0, column = 0, sticky = "NSEW")

		info_frame = ttk.Frame(main_frame, padding = 5)
		info_frame.grid(row = 0, column = 1, sticky = "NSEW")
		info_frame.grid_rowconfigure(0, weight = 1)
		info_frame.grid_rowconfigure(1, weight = 3)
		info_frame.grid_rowconfigure(2, weight = 4)
		info_frame.grid_columnconfigure(0, weight = 1)
		self.food = tk.StringVar(value= "Apples")

# --- WIDGETS ---

		titleLbl = ttk.Label(title_frame, text = "Confirmation", style = "NormalText.TLabel", padding = 20)
		imgLbl = ttk.Label(image_frame, image = self.preview, padding = 20)
		titlefoodLbl = ttk.Label(info_frame, text = "Is it.... ?", style = "NormalText2.TLabel", padding = 5)
		foodLbl = ttk.Label(info_frame, textvariable = self.food, style = "BigText.TLabel", padding = 5)
		foodinfoLbl = ttk.Label(info_frame, text = "Waste info: ", style = "NormalText2.TLabel", padding = 5)
		yesbtn = ttk.Button(button_container, text = "Correct!",style = "YesButton.TButton", padding = 10, command = controller.dump_waste)
		nobtn = ttk.Button(button_container, text = "No", style = "NoButton.TButton", padding = 10, command = controller.dump_waste)

# --- LAYOUTS ---
		
		titleLbl.grid(row = 0, column = 0, sticky = "NSEW")
		imgLbl.grid(row = 0 , column = 0, sticky = "NSEW")
		titlefoodLbl.grid(row = 0, column = 0, sticky = "W")
		foodLbl.grid(row = 1, column = 0 , sticky = "NSEW", padx = (100,0))
		foodinfoLbl.grid(row = 2, column = 0, sticky = "W")
		yesbtn.pack(side = "right", padx = 20, pady = 5)
		nobtn.pack(side = "right", padx = 20, pady = 5)


#----------------------------MAIN PROGRAM-----------------------------#

root = StadaAPP()	
root.after(500, root.refresh_frame)
root.mainloop()

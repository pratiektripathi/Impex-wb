#!/usr/bin/env python3
import asyncio
import datetime
import multiprocessing
import queue as q
import subprocess
import cv2
import requests
import numpy as np
from io import BytesIO
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk
from tkinter.font import Font
import serial

from PIL import Image, ImageTk
import db
from tkcalendar import DateEntry
from picHandler import PicHandler
import report2

import zebrapl
import pandas as pd
xuid=0

try:
    chuid=int(db.Lcheck())
    
    if chuid==1:
        xuid = 1
    else:
        xuid = 0
except:
    xuid = 0




xcom=[]

try:
    xcom=db.loadcom()
except:
    xcom=["IMPEX CORPORATION WEIGH BRIDGE",
            "Ispat Nadar, Vyapar Nagar, Kanpur",
            "Mo. : 9719095897, 9839347986",
            "Graphics Printer",
            "Disable",
            1,
            2,
            "",
            "COM1",
            19200,
            "",
            5,
          0,
          0,
           "res/nocam.jpg",
            "res/nocam.jpg",
            0]

CN=xcom[1]
A_1=xcom[2]
A_2=xcom[3]
P_T=xcom[4]
SWP=xcom[5]
NCPF1=xcom[6]
NCPF2=xcom[7]
DP=xcom[8]
com=xcom[9]
baurd=int(xcom[10])
rfind=xcom[11]
WDL=int(xcom[12])

rshift=int(xcom[13])
camEN=int(xcom[14])
IPcam1=xcom[15]
IPcam2=xcom[16]
picEN=xcom[17]



class SerialThread(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue

    def run(self):


        try:
            s = serial.Serial(com,baurd, timeout=2)
            while True:

                k = s.readline().decode('utf-8')

                if rfind!="":
                    c=k.find(rfind)
                    k=k[:c]

                k=k[-1*WDL:len(k)-rshift]
                text=k.replace(" ","")
                # text = k
                self.queue.put(text)

        except:
            self.queue.put("ComErr")

class LoginWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Login")
        self.iconbitmap("myicon.ico")
        self.overrideredirect(True)



        # Get the screen width and height
        xcord=(self.winfo_screenwidth()/4)
        ycord=(self.winfo_screenheight()/4)
        window_width=int((self.winfo_screenwidth()/2))
        window_height=int((self.winfo_screenheight()/2))
        self.geometry(f"{window_width}x{window_height}+{int(xcord)}+{int(ycord)}")

        l_font = Font(family="Arial", size=12, weight="bold")
        e_font = Font(family="Arial", size=10)



        # Load the background image
        image = Image.open("bgi.png")
        image = image.resize((window_width, window_height))
        self.background_image = ImageTk.PhotoImage(image)

        canvas1 = tk.Canvas(self, width=window_width, height=window_height)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.background_image, anchor="nw")

        # Create a frame to hold the labels and entry fields
        frame = tk.Frame(canvas1,bg="#FAC829")
        frame.place(x=540, rely=0.5, anchor="center")

        # Create the username and password labels
        self.label_username = tk.Label(frame, text="Username:",font=l_font,fg="#36444D", bg="#FAC829")
        self.label_username.grid(row=0, column=0, padx=5, pady=10, sticky="e")

        self.label_password = tk.Label(frame, text="Password:",font=l_font,fg="#36444D", bg="#FAC829")
        self.label_password.grid(row=1, column=0, padx=5, pady=10, sticky="e")



        # Create the username and password entry fields
        self.entry_username = tk.Entry(frame,font=e_font, width=16)
        self.entry_username.grid(row=0, column=1, pady=10)


        self.entry_password = tk.Entry(frame,font=e_font, show="*", width=16)
        self.entry_password.grid(row=1, column=1, pady=10)


        self.button_login = tk.Button(frame,relief="groove", text="Login", fg="#36444D", bg="#FAC829",font=l_font, command=self.login)
        self.button_login.grid(row=2, column=0, columnspan=3,padx=10, pady=10)

        # Create a close button
        self.button_close = tk.Button(frame,relief="groove", text="Close",fg="#36444D", bg="#FAC829",font=l_font, command=self.close_window)
        self.button_close.grid(row=2, column=1, columnspan=3,padx=10, pady=10,sticky="e")

        self.entry_username.focus_set()
        self.entry_username.bind("<Return>", lambda event: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda event: self.login())


    def close_window(self):
        self.destroy()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Add your logic for login authentication
        # For example, you can check if the username and password are correct
        if username == "admin" and password == "admin":
            tk.messagebox.showinfo("Login Successful", "You have successfully logged in!")
            self.destroy()
            app = MainApp()

            SerialThread.daemon=True
            




        else:
            tk.messagebox.showerror("Login Failed", "Invalid username or password")



class MainApp(tk.Tk):



    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        if xuid==1:
            self.title("Impex IMP-WB v1.5 (Activated)")
        else:
            self.title("Impex IMP-WB v1.5(demo)")

        self.iconbitmap('myicon.ico')
        window_width=int((self.winfo_screenwidth()))
        window_height=int((self.winfo_screenheight()))
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(False,True)
        self.state('zoomed')



        frame1 = tk.Frame(self,bg="#FFF5EE")


        weight_font = Font(family="Arquitecta", size=80)
        Label1_font = Font(family="Arquitecta", size=15)
        Label2_font = Font(family="Arquitecta", size=15)

        self.bind("<Escape>", lambda e: self.ext())
        self.bind("<Alt_L>" + "<F9>", lambda e: self.destroy())



        self.errtext = tk.StringVar()

        self.hero = tk.StringVar()

        self.TempValue = tk.StringVar()
        self.curentframe = tk.StringVar()
        

        # logo
        framelogo = tk.Frame(frame1,bg="#FFF5EE")
        im = Image.open('new_impex_logo.gif')

        resized = im.resize((420, 100), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)
        labellogo = tk.Label(framelogo, image=self.image,bg="#FFF5EE")
        labellogo.pack()
        framelogo.grid(row=0, column=0, rowspan=2)

        frame1.grid_columnconfigure(2, weight=1)



        frame_weight = tk.Frame(frame1,bg="#FFF5EE")

        self.label3 = tk.Label(frame_weight, textvariable=self.TempValue, bg="black", fg="#00FF00", font=weight_font,
                               width=8, justify='center')
        self.label3.pack(side='left', padx=0)

        self.Label2 = tk.Label(frame_weight, text="Kg.", fg="black",bg="#FFF5EE", font=Label2_font).pack(side='left',
                                                                                                        padx=5, pady=0,
                                                                                                        anchor='s')
        frame_weight.grid(row=0, column=4, rowspan=2, columnspan=2, sticky='E')


        frame1.pack(anchor="n", fill="both", expand=True)


        self.errlabel = tk.Label(frame1, textvariable=self.errtext, fg="red", bg='white', font=Label1_font)
        self.errlabel.grid(row=13, column=2, columnspan=2, padx=6, pady=10)


        frame1.grid_rowconfigure(11, weight=1)

        container = tk.Frame(frame1,bg="#FFF5EE")

        container.grid(row=3, column=0, rowspan=4, columnspan=5)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageFive,PageManual):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(StartPage)
        if camEN==1:
            self.create_cam_page()


        if xuid==1:
            self.queue = multiprocessing.Queue()
            self.thread = SerialThread(self.queue)
            self.thread.start()
            self.process_serial()

        else:
            self.TempValue.set("VerErr")


    def create_cam_page(self):
        self.cam_page = CamPage(self)


    def ext(self):
        self.frames[PageOne].close()
        self.frames[PageTwo].close()


        self.frames[PageFive].close()
        self.frames[PageManual].close()













    def reconwt(self):
        self.queue = multiprocessing.Queue()
        self.thread = SerialThread(self.queue)
        self.thread.start()


    def process_serial(self):
        while self.queue.qsize():
            try:
               data= self.queue.get()
               if (data=='Err') :
                   self.TempValue.set("Err")


               elif (data=='.'):
                   self.TempValue.set("------")


               else:
                   self.TempValue.set(str(data))



            except q.Empty():
                self.TempValue.set("------")
                pass

        self.after(500, self.process_serial)




    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        self.hero.set(cont)



class CamPage(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.geometry("+500+0")
        self.iconbitmap('myicon.ico')
        self.focus_set()
        self.title("IP camera")

        frame2 = tk.Frame(self, bg='white')

        Label_font = Font(family="Arquitecta", size=14)



        cam_frame1 = tk.LabelFrame(frame2, text="Front",  bg='white', font=Label_font)
        cam_frame1.grid(row=0, column=0,padx=0, ipady=0)
        self.camera_label1 = tk.Label(cam_frame1)
        self.camera_label1.grid(row=0, column=0, padx=0, pady=0, sticky='w')

        cam_frame2 = tk.LabelFrame(frame2, text="back",  bg='white', font=Label_font)
        cam_frame2.grid(row=0, column=1,padx=0, ipady=0)
        self.camera_label2 = tk.Label(cam_frame2)
        self.camera_label2.grid(row=0, column=0, padx=0, pady=0, sticky='w')



        frame2.pack(fill='both',expand=True)

        # Call the function to download and display the IP camera image
        self.download_and_display_camera_image1()
        self.download_and_display_camera_image2()




    def download_and_display_camera_image1(self):
        try:
            image_url1 = IPcam1
            response1 = requests.get(image_url1, stream=True)
           

            if response1.status_code == 200:
                image_data = BytesIO(response1.content)
                image_array = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                # Resize the image to your desired dimensions
                target_width = 150 # Adjust this width as needed
                target_height = 90  # Adjust this height as needed
                resized_image = cv2.resize(image, (target_width, target_height))

                pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
                tk_image = ImageTk.PhotoImage(pil_image)

                # Update the image in the camera label
                self.camera_label1.configure(image=tk_image)
                self.camera_label1.image = tk_image  # Keep a reference to the image

                self.camera_label1.after(200, self.download_and_display_camera_image1)


            else:
                default_image = Image.open("res/nocam.jpg")
                tk_default_image = ImageTk.PhotoImage(default_image)

                # Update the image in the camera label with the default image
                self.camera_label1.configure(image=tk_default_image)
                self.camera_label1.image = tk_default_image # Keep a reference to the image
        
            

        except:
            default_image = Image.open("res/nocam.jpg")
            tk_default_image = ImageTk.PhotoImage(default_image)

            # Update the image in the camera label with the default image
            self.camera_label1.configure(image=tk_default_image)
            self.camera_label1.image = tk_default_image  # Keep a reference to the image


       
    def download_and_display_camera_image2(self):
        try:
            image_url2 = IPcam2
            response2 = requests.get(image_url2, stream=True)
           

            if response2.status_code == 200:
                image_data = BytesIO(response2.content)
                image_array = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                # Resize the image to your desired dimensions
                target_width = 150 # Adjust this width as needed
                target_height = 90  # Adjust this height as needed
                resized_image = cv2.resize(image, (target_width, target_height))

                pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
                tk_image = ImageTk.PhotoImage(pil_image)

                # Update the image in the camera label
                self.camera_label2.configure(image=tk_image)
                self.camera_label2.image = tk_image  # Keep a reference to the image

                self.camera_label2.after(200, self.download_and_display_camera_image2)


            else:
                default_image = Image.open("res/nocam.jpg")
                tk_default_image = ImageTk.PhotoImage(default_image)

                # Update the image in the camera label with the default image
                self.camera_label2.configure(image=tk_default_image)
                self.camera_label2.image = tk_default_image # Keep a reference to the image
        
            

        except:
            default_image = Image.open("res/nocam.jpg")
            tk_default_image = ImageTk.PhotoImage(default_image)

            # Update the image in the camera label with the default image
            self.camera_label2.configure(image=tk_default_image)
            self.camera_label2.image = tk_default_image  # Keep a reference to the image


        self.protocol("WM_DELETE_WINDOW", self.recreate_cam_page)



    def recreate_cam_page(self):
        # Destroy the current CamPage instance
        parent = self.master
        # Destroy the current CamPage instance
        self.destroy()
        # Recreate a new CamPage instance in the parent
        parent.create_cam_page()







class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg="#FFF5EE")
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)


        treeview_width = int((self.winfo_screenwidth())/1.6)
        # Create the button frame on the left side
        button_frame = tk.Frame(self, bg="#FFF5EE")
        button_frame.grid(row=0, column=0, sticky="nsew")


        # Create the Treeview frame on the right side
        treeview_frame = tk.Frame(self,width=treeview_width,bg="#FFF5EE")
        treeview_frame.grid(row=0, column=1,padx=2,pady=2, sticky="nsew")


        title_label = tk.Label(treeview_frame, text="PENDING TRANSACTIONS",bg="#FFF5EE", font=("Arial", 16,"bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


        # Configure grid weights for button_frame and treeview_frame
        button_frame.columnconfigure(0, weight=1)
        button_frame.rowconfigure(0, weight=1)
        treeview_frame.columnconfigure(0, weight=1)
        treeview_frame.rowconfigure(0, weight=1)


        # Create button images
        image1 = Image.open("res/first_weight.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/second_weight.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/final_weight.jpg")
        button_image3 = ImageTk.PhotoImage(image3)

        image4 = Image.open("res/Reports.jpg")
        button_image4 = ImageTk.PhotoImage(image4)


        image5 = Image.open("res/print_view.jpg")
        button_image5 = ImageTk.PhotoImage(image5)

        # Create buttons in the button frame
        button1 = tk.Button(button_frame, relief="groove", image=button_image1, compound="left",command=lambda:self.F1_Page())
        button1.image = button_image1  # Store the image reference
        button1.bind("<Return>", lambda e: self.F1_Page())
        button1.pack(side="top", padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.F2_Page())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.F2_Page())
        button2.pack(side="top", padx=10, pady=10)

        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.F5_Page())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.F5_Page())
        button3.pack(side="top", padx=10, pady=10)

        button45_frame = tk.Frame(button_frame,bg="#FFF5EE")
        button45_frame.pack(side="top")

        # Create button4 and button5 in the button45_frame
        button4 = tk.Button(button45_frame, relief="groove", image=button_image4, compound="left",command=lambda :self.reporter())
        button4.image = button_image4  # Store the image reference
        button4.bind("<Return>", lambda e: self.reporter())
        button4.pack(side="left", padx=10, pady=10)

        button5 = tk.Button(button45_frame, relief="groove", image=button_image5, compound="left",command=lambda :self.printview())
        button5.image = button_image5  # Store the image reference
        button5.pack(side="left", padx=10, pady=10)
        button4.bind("<Return>", lambda e: self.printview())
        # Create a vertical scrollbar for the Treeview

        self.treeview = ttk.Treeview(treeview_frame, columns=("Sno","TicketNo",
            "VehicleNo", "VehicleType", "PartyName", "Charges", "Material",
            "GrossWeight", "TareWeight", "GrossWeightDate", "GrossWeightTime",
            "TareWeightDate", "TareWeightTime"
        ))
        self.treeview.grid(row=1, column=0, sticky="nsew")
        self.treeview.column("#0",width=0, stretch=False, anchor="center")

        self.treeview.column("Sno", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("TicketNo", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("VehicleNo", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("VehicleType", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("PartyName", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("Charges", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("Material", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeight", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeight", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeightDate", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeightTime", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeightDate", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeightTime", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")

        # Add headings
        self.treeview.heading("Sno", text="S No.")
        self.treeview.heading("TicketNo", text="Ticket No.")
        self.treeview.heading("VehicleNo", text="Vehicle No.")
        self.treeview.heading("VehicleType", text="Vehicle Type")
        self.treeview.heading("PartyName", text="Party Name")
        self.treeview.heading("Charges", text="Charges")
        self.treeview.heading("Material", text="Material")
        self.treeview.heading("GrossWeight", text="Gross Weight")
        self.treeview.heading("TareWeight", text="Tare Weight")
        self.treeview.heading("GrossWeightDate", text="Gross Weight Date")
        self.treeview.heading("GrossWeightTime", text="Gross Weight Time")
        self.treeview.heading("TareWeightDate", text="Tare Weight Date")
        self.treeview.heading("TareWeightTime", text="Tare Weight Time")

        self.treeview.bind("<Double-1>",lambda e:self.show_messagebox())


        self.refresh()

        scrollbar_y = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_y.grid(row=1, column=1, sticky="ns")
        self.treeview.configure(yscrollcommand=scrollbar_y.set)

        # Create the horizontal scrollbar
        scrollbar_x = ttk.Scrollbar(treeview_frame, orient="horizontal", command=self.treeview.xview)
        scrollbar_x.grid(row=2, column=0, sticky="ew")
        self.treeview.configure(xscrollcommand=scrollbar_x.set)

        image6 = Image.open("res/settings.jpg")
        button_image6 = ImageTk.PhotoImage(image6)

        button6 = tk.Button(self,relief="groove", image=button_image6, compound="left", command=lambda :self.open_setting())
        button6.image = button_image6  # Store the image reference
        button6.grid(row=2, column=1,sticky="es")


        style = ttk.Style()
        style.configure("Treeview.Item", font=("Arial", 16))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))



        # Configure the treeview frame to restrict its width and enable horizontal scrolling
        treeview_frame.grid_propagate(False)
        treeview_frame.grid_rowconfigure(0, weight=1)
        treeview_frame.grid_columnconfigure(0, weight=1)
        treeview_frame.grid_rowconfigure(0, weight=0)  # Title label row
        treeview_frame.grid_rowconfigure(1, weight=1)  # Treeview row
        treeview_frame.grid_columnconfigure(0, weight=1)  # Single column



    def open_setting(self):
        window=PassWindow(self)
        window.grab_set()


    def printview(self):
        window=PrintViewPage(self)
        window.grab_set()


    def show_messagebox(self):
        item = self.treeview.focus()
        item_text = self.treeview.item(item, "values")
        column1_name = item_text[1]
        msg = tk.messagebox.askquestion("Complete Transection ?",f"DO YOU WANT TO COMPLETE  TICKET No.: {column1_name}")
        if msg=="yes":
            self.F2_Page()
            self.controller.frames[PageTwo].field1.set(column1_name)
            self.controller.frames[PageTwo].gettktdetails()



    def F1_Page(self):
        self.controller.frames[PageOne].F1()

    def F2_Page(self):
        self.controller.frames[PageTwo].F2()

    def F5_Page(self):
        self.controller.frames[PageFive].F5()


    def refresh(self):
        # Clear existing data in the treeview
        self.treeview.delete(*self.treeview.get_children())

        # Fetch data from the database
        data = db.fetch_data()

        for index, row in enumerate(data, start=1):
            # Insert the row values at the corresponding columns
            self.treeview.insert("", "end", values=(index,) + row)


    def reporter(self):
        window=Report(self)
        window.grab_set()




class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        frame2 = tk.Frame(self, bg='#FFF5EE')

        self.field01 = tk.StringVar()
        self.field02 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()
        self.field5 = tk.StringVar()
        self.field6 = tk.StringVar()
        self.field7 = tk.StringVar()
        self.field8 = tk.StringVar()
        self.field9 = tk.StringVar()
        self.field10 = tk.StringVar()
        self.label07 = tk.StringVar()

        self.controller = controller

        Label_font = Font(family="Arquitecta", size=16, weight="bold")
        field_font = Font(family="Arquitecta", size=18)
        field5font = Font(family="Arquitecta", size=32, weight="bold")
        field1font = Font(family="Arquitecta", size=25, weight="bold")



        frame2.pack(fill='both', expand=True,anchor="center")

        # Create a LabelFrame
        label_frame = tk.LabelFrame(frame2, text="Details",bg='#FFF5EE',font=Label_font)
        label_frame.grid(row=1,column=0,pady=20,ipady=10,rowspan=2,sticky="E")

        # Create Labels and corresponding Entry fields
        labels = ["Date/Time :", "Ticket No :", "Vehicle No :", "Vehicle Type :",
                  "Party Name :", "Material :", "Charges :", "Gross(G)/Tare(T) :","Gross Weight :", "Tare Weight :",
                  "Net Weight :"]

        self.label_0 = tk.Label(label_frame, text=labels[0], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_0.grid(row=5, column=2, padx=25, pady=0, sticky='w')
        self.field_01 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field01, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_01.grid(row=5, column=3, padx=20, pady=0, sticky='w')

        self.field_02 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field02, width=8,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_02.grid(row=5, column=4, padx=0, pady=0, sticky='w')




        self.label_1 = tk.Label(label_frame, text=labels[1], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_1.grid(row=6, column=2, padx=20, pady=0, sticky='w')
        self.field_1 = tk.Entry(label_frame, disabledforeground="red", bg='white', textvariable=self.field1, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field1font, justify='center',
                                exportselection=False)
        self.field_1.bind("<Return>", lambda e: self.field_2.focus_set())
        self.field_1.grid(row=6, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.label_2 = tk.Label(label_frame, text=labels[2], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_2.grid(row=7, column=2, padx=20, pady=0, sticky='w')
        self.field_2 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field2, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_2.bind("<Return>", lambda e: self.field_3.focus_set())
        self.field_2.grid(row=7, column=3, padx=20, pady=0, columnspan=2)

        self.label_3 = tk.Label(label_frame, text=labels[3], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_3.grid(row=8, column=2, padx=20, pady=0, sticky='w')
        self.field_3 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field3, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_3.bind("<Return>", lambda e: self.field_4.focus_set())
        self.field_3.grid(row=8, column=3, padx=20, pady=0, columnspan=2)

        self.label_4 = tk.Label(label_frame, text=labels[4], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_4.grid(row=9, column=2, padx=20, pady=0, sticky='w')
        self.field_4 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field4, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_4.bind("<Return>", lambda e: self.field_5.focus_set())
        self.field_4.grid(row=9, column=3, padx=20, pady=0, columnspan=2)

        self.label_5 = tk.Label(label_frame, text=labels[5], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_5.grid(row=10, column=2, padx=20, pady=0, sticky='w')
        self.field_5 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field5, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_5.bind("<Return>", lambda e: self.field_6.focus_set())
        self.field_5.grid(row=10, column=3, padx=20, pady=0, columnspan=2)

        self.label_6 = tk.Label(label_frame, text=labels[6], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_6.grid(row=11, column=2, padx=20, pady=0, sticky='w')
        self.field_6 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field6, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)

        self.field_6.bind("<Return>", lambda e: self.field_7.focus_set())
        self.field_6.grid(row=11, column=3, padx=20, pady=0, columnspan=2)

        self.label_7 = tk.Label(label_frame, text=labels[7], fg="black",bg='#FFF5EE', font=Label_font)
        self.label_7.grid(row=12, column=2, padx=20, pady=0, sticky='w')

        frame_field7=tk.Frame(label_frame,bg="#FFF5EE")
        frame_field7.grid(row=12, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.field_7 = tk.Entry(frame_field7, fg="black", bg='white', textvariable=self.field7, width=2,
                                highlightthickness=2, highlightcolor='yellow', font=field5font, justify='center',
                                exportselection=False)
        self.field_7.bind("<Return>", lambda e: self.setweight())
        self.field_7.grid(row=0, column=0,padx=20, pady=0, sticky='w')
        self.label_07 = tk.Label(frame_field7, textvariable=self.label07, fg="black",bg='#FFF5EE', font=field5font)
        self.label_07.grid(row=0, column=1, pady=0, sticky='e')



        label_frame1 = tk.LabelFrame(frame2, text="Weight",  bg='#FFF5EE', font=Label_font)
        label_frame1.grid(row=1, column=1,padx=50, ipady=10)

        self.label_8 = tk.Label(label_frame1, text=labels[8], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_8.grid(row=0, column=0, padx=20, pady=0, sticky='w')
        self.field_8 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field8, width=20,
                            highlightthickness=2, highlightcolor='yellow',font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_8.grid(row=0, column=1, padx=20, pady=0)

        self.label_9 = tk.Label(label_frame1, text=labels[9], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_9.grid(row=1, column=0, padx=20, pady=0, sticky='w')
        self.field_9 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field9, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_9.grid(row=1, column=1, padx=20, pady=0)



        button_frame = tk.Frame(frame2, bg='#FFF5EE')
        button_frame.grid(row=2,column=1,padx=50,pady=10,sticky="nsew")

        image1 = Image.open("res/save.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/exit.jpg")
        button_image3 = ImageTk.PhotoImage(image3)



        self.button1 = tk.Button(button_frame,relief="groove", image=button_image1, compound="left",command=lambda :self.asktosave())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.asktosave())
        self.button1.grid(row=0,column=0, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=1, padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.close())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.close())
        button3.grid(row=0,column=2, padx=10, pady=10)






        self.field01.trace('w', lambda *args: self.auto_capitalize(self.field01))
        self.field02.trace('w', lambda *args: self.auto_capitalize(self.field02))
        self.field1.trace('w', lambda *args: self.auto_capitalize(self.field1))
        self.field2.trace('w', lambda *args: self.auto_capitalize(self.field2))
        self.field3.trace('w', lambda *args: self.auto_capitalize(self.field3))
        self.field4.trace('w', lambda *args: self.auto_capitalize(self.field4))
        self.field5.trace('w', lambda *args: self.auto_capitalize(self.field5))
        self.field7.trace('w', lambda *args: self.auto_capitalize(self.field7))


        self.validation6=self.register(self.validate_field_6)
        self.field_6.config(validate='key',validatecommand=(self.validation6,'%P'))

        self.validation7=self.register(self.validate_field_7)
        self.field_7.config(validate='key',validatecommand=(self.validation7,'%P'))





        self.controller.bind("<F1>", lambda e: self.F1())

    

    def auto_capitalize(self, variable):
        value = variable.get()
        variable.set(value.upper())

    def validate_field_7(self, value):

        # Validation function to restrict input in field_7 to 'T' or 'G' only
        return value.upper() in ['T', 'G','']

    def validate_field_6(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False




    def F1(self):
        try:
            if (self.controller.hero.get()=="<class '__main__.StartPage'>"):
                self.controller.show_frame(PageOne)
                self.clr()
                self.field_2.focus_set()

        except:
            pass


    def asktosave(self):
        wt=self.controller.TempValue.get()
        if self.field7.get()=="T" :
            self.field7.set("T")
            self.field9.set(wt)
            self.field8.set("")
            self.label07.set("Tare")
            self.tosave()

        elif self.field_7.get()=="":
            self.field7.set("T")
            self.field9.set(wt)
            self.field8.set("")
            self.button1.focus_set()



        elif self.field7.get()=="G" and int(wt)>0 :
            self.field8.set(wt)
            self.field9.set("")
            self.tosave()

        elif self.field7.get()=="G" and int(wt)<=0 :
            tk.messagebox.showerror("Error","GROSS WEIGHT must be greater than 0 put some weight on platform")
            self.field7.set("")
            self.field_7.focus_set()





    def tosave(self):
        Label_font = Font(family="Arquitecta", size=16, weight="bold")

        save_image = Image.open("res/save.jpg")
        save_photo = ImageTk.PhotoImage(save_image)

        # Load the print icon image
        print_image = Image.open("res/print.jpg")
        print_photo = ImageTk.PhotoImage(print_image)

        close_image = Image.open("res/exit.jpg")
        close_photo = ImageTk.PhotoImage(close_image)

        # Create a custom dialog window
        self.dialog = tk.Toplevel(bg="white")
        self.dialog.title("Save, Print, or Close")
        self.dialog.iconbitmap("myicon.ico")
        # Display the message
        message_label = tk.Label(self.dialog, text=" Save, Print, or Close",font=Label_font,bg="white")
        message_label.pack(padx=20, pady=10)


        save_button = tk.Button(self.dialog, image=save_photo, compound="left", command=lambda : self.save())
        save_button.image = save_photo
        save_button.bind("<Return>",lambda e:self.save())
        save_button.pack(side='left',padx=10, pady=5)



        # Create buttons with icons
        print_button = tk.Button(self.dialog, image=print_photo, compound="left",command=lambda :self.save("print"))
        print_button.image = print_photo
        print_button.bind("<Return>",lambda e:self.save("print"))
        print_button.pack(side='left',padx=10, pady=5)

        close_button = tk.Button(self.dialog, image=close_photo, command=self.dialog.destroy)
        close_button.image = close_photo
        close_button.pack(side='left',padx=10, pady=5)


        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        dialog_width = 500  # Adjust the width of the dialog box as needed
        dialog_height = 200  # Adjust the height of the dialog box as needed
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        save_button.focus_set()




    def save(self,pp=None):

        VehicleNo=self.field_2.get()
        VehicleType=self.field_3.get()
        PartyName=self.field_4.get()
        Charges=self.field_6.get()
        Material=self.field_5.get()
        GrossWeight=self.field_8.get()
        TareWeight=self.field_9.get()
        Final=self.field_7.get()
        pic_handler = PicHandler()
        url1 = IPcam1
        filename1 = f"camera/front/{self.field_1.get()}_1.jpg"
        url2 = IPcam2
        filename2 = f"camera/back/{self.field_1.get()}_1.jpg"



        if self.field_7.get()=="T" :
            GrossWeightDate=""
            GrossWeightTime=""
            TareWeightDate=self.field_01.get()
            TareWeightTime=self.field_02.get()
        else:
            GrossWeightDate=self.field_01.get()
            GrossWeightTime=self.field_02.get()
            TareWeightDate=""
            TareWeightTime=""

        savedata=[VehicleNo,VehicleType,PartyName,Charges,
                Material,GrossWeight,TareWeight,GrossWeightDate,
                  GrossWeightTime,TareWeightDate,TareWeightTime,Final,"","",""]

        try:
            db.SaveWbData(savedata)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(pic_handler.download_images(url1, filename1, url2, filename2))
            tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
            if pp=="print":
                savedata.insert(0, self.field_1.get())
                try:
                    zebrapl.print_ticket(savedata,"original","")
                except:
                    tk.messagebox.showerror("Print Error","Unable to Initialize printer.")

        except:
            tk.messagebox.showerror("Error Save","DATABASE ERROR please try again.")


        
        self.dialog.destroy()
        self.controller.frames[StartPage].refresh()
        self.close()





    def clr(self):
        self.field01.set(datetime.date.today().strftime("%d-%m-%Y"))
        self.field02.set(datetime.datetime.now().strftime("%H:%M:%S"))
        rst=db.lastRst()
        if rst==None:
            self.field1.set("1")
        else:
            self.field1.set(rst+1)

        self.field2.set("")
        self.field3.set("")
        self.field4.set("")
        self.field5.set("")
        self.field6.set("")
        self.field7.set("")
        self.field8.set("")
        self.field9.set("")
        self.label07.set("")




    def setweight(self):
        wt=self.controller.TempValue.get()
        if self.field7.get()=="T" or self.field_7.get()=="":
            self.field7.set("T")
            self.label07.set("Tare")
            self.field9.set(wt)
            self.field8.set("")
            self.button1.focus_set()



        elif self.field7.get()=="G" and int(wt)>0 :
            self.field8.set(wt)
            self.label07.set("Gross")
            self.field9.set("")
            self.button1.focus_set()

        elif self.field7.get()=="G" and int(wt)<=0 :
            tk.messagebox.showerror("Error","GROSS WEIGHT must be greater than 0 put some weight on platform")
            self.field7.set("")
            self.field_7.focus_set()



    def close(self):
        self.clr()
        self.controller.show_frame(StartPage)
        self.controller.focus_set()



class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        frame2 = tk.Frame(self, bg='#FFF5EE')

        self.field01 = tk.StringVar()
        self.field02 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()
        self.field5 = tk.StringVar()
        self.field6 = tk.StringVar()
        self.field8 = tk.StringVar()
        self.field9 = tk.StringVar()
        self.field10 = tk.StringVar()
        self.field11=tk.StringVar()

        self.controller = controller

        Label_font = Font(family="Arquitecta", size=16, weight="bold")
        field_font = Font(family="Arquitecta", size=18)
        field5font = Font(family="Arquitecta", size=32, weight="bold")
        field1font = Font(family="Arquitecta", size=25, weight="bold")



        frame2.pack(fill='both', expand=True,anchor="center")

        # Create a LabelFrame
        label_frame = tk.LabelFrame(frame2, text="Details",bg='#FFF5EE',font=Label_font)
        label_frame.grid(row=1,column=0,pady=20,ipady=10,rowspan=2,sticky="E")

        # Create Labels and corresponding Entry fields
        labels = ["Date/Time :", "Ticket No :", "Vehicle No :", "Vehicle Type :",
                  "Party Name :", "Material :", "Charges :", "F2 Final Weight","Gross Weight :", "Tare Weight :",
                  "Net Weight :"]

        self.label_0 = tk.Label(label_frame, text=labels[0], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_0.grid(row=5, column=2, padx=25, pady=0, sticky='w')
        self.field_01 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field01, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_01.grid(row=5, column=3, padx=20, pady=0, sticky='w')

        self.field_02 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field02, width=8,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_02.grid(row=5, column=4, padx=0, pady=0, sticky='w')




        self.label_1 = tk.Label(label_frame, text=labels[1], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_1.grid(row=6, column=2, padx=20, pady=0, sticky='w')
        self.field_1 = tk.Entry(label_frame, fg="red", bg='white', textvariable=self.field1, width=10,
                                highlightthickness=2, highlightcolor='yellow', font=field1font, justify='center',
                                exportselection=False)
        self.field_1.bind("<Return>", lambda e: self.gettktdetails())
        self.field_1.grid(row=6, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.label_2 = tk.Label(label_frame, text=labels[2], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_2.grid(row=7, column=2, padx=20, pady=0, sticky='w')
        self.field_2 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field2, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_2.bind("<Return>", lambda e: self.field_3.focus_set())
        self.field_2.grid(row=7, column=3, padx=20, pady=0, columnspan=2)

        self.label_3 = tk.Label(label_frame, text=labels[3], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_3.grid(row=8, column=2, padx=20, pady=0, sticky='w')
        self.field_3 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field3, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_3.bind("<Return>", lambda e: self.field_4.focus_set())
        self.field_3.grid(row=8, column=3, padx=20, pady=0, columnspan=2)

        self.label_4 = tk.Label(label_frame, text=labels[4], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_4.grid(row=9, column=2, padx=20, pady=0, sticky='w')
        self.field_4 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field4, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_4.bind("<Return>", lambda e: self.field_5.focus_set())
        self.field_4.grid(row=9, column=3, padx=20, pady=0, columnspan=2)

        self.label_5 = tk.Label(label_frame, text=labels[5], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_5.grid(row=10, column=2, padx=20, pady=0, sticky='w')
        self.field_5 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field5, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)
        self.field_5.bind("<Return>", lambda e: self.field_6.focus_set())
        self.field_5.grid(row=10, column=3, padx=20, pady=0, columnspan=2)

        self.label_6 = tk.Label(label_frame, text=labels[6], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_6.grid(row=11, column=2, padx=20, pady=0, sticky='w')
        self.field_6 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field6, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=False)

        self.field_6.grid(row=11, column=3, padx=20, pady=0, columnspan=2)

        self.label_7 = tk.Label(label_frame, text=labels[7], fg="grey",bg='#FFF5EE', font=field5font)
        self.label_7.grid(row=12, column=2, padx=20, pady=0, sticky='w',columnspan=2)


        label_frame1 = tk.LabelFrame(frame2, text="Weight",  bg='#FFF5EE', font=Label_font)
        label_frame1.grid(row=1, column=1,padx=50, ipady=10)

        self.label_8 = tk.Label(label_frame1, text=labels[8], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_8.grid(row=0, column=0, padx=20, pady=0, sticky='w')
        self.field_8 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field8, width=20,
                            highlightthickness=2, highlightcolor='yellow',font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_8.grid(row=0, column=1, padx=20, pady=0)

        self.label_9 = tk.Label(label_frame1, text=labels[9], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_9.grid(row=1, column=0, padx=20, pady=0, sticky='w')
        self.field_9 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field9, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_9.grid(row=1, column=1, padx=20, pady=0)


        self.label_10 = tk.Label(label_frame1, text=labels[10], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_10.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.field_10 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field10, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_10.grid(row=2, column=1, padx=20, pady=0)



        button_frame = tk.Frame(frame2, bg='#FFF5EE')
        button_frame.grid(row=2,column=1,padx=50,pady=10,sticky="nsew")

        image1 = Image.open("res/save.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/exit.jpg")
        button_image3 = ImageTk.PhotoImage(image3)



        self.button1 = tk.Button(button_frame,relief="groove", image=button_image1, compound="left",command=lambda:self.asktosave())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.asktosave())
        self.button1.grid(row=0,column=0, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=1, padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.close())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.close())
        button3.grid(row=0,column=2, padx=10, pady=10)




        self.field01.trace('w', lambda *args: self.auto_capitalize(self.field01))
        self.field02.trace('w', lambda *args: self.auto_capitalize(self.field02))
        self.field2.trace('w', lambda *args: self.auto_capitalize(self.field2))
        self.field3.trace('w', lambda *args: self.auto_capitalize(self.field3))
        self.field4.trace('w', lambda *args: self.auto_capitalize(self.field4))
        self.field5.trace('w', lambda *args: self.auto_capitalize(self.field5))


        self.validation6=self.register(self.validate_field_6)
        self.field_6.config(validate='key',validatecommand=(self.validation6,'%P'))
        self.field_1.config(validate='key',validatecommand=(self.validation6,'%P'))







        self.controller.bind("<F2>", lambda e: self.F2())



    def unDisable(self):
        self.field_1.config(state="disabled")
        self.field_2.config(state="normal")
        self.field_3.config(state="normal")
        self.field_4.config(state="normal")
        self.field_5.config(state="normal")
        self.field_6.config(state="normal")




    def gettktdetails(self):
        try:
            id=self.field1.get()
            data=db.getsecond(id)
            self.tktdetails(data)
        except:
            tk.messagebox.showerror("ERROR","Please Enter Valid Ticket No.")

    def tktdetails(self,data):
        pd=list(data)
        wt=self.controller.TempValue.get()
        if pd[12] in ["G","T"] :
            self.field2.set(pd[1])
            self.field3.set(pd[2])
            self.field4.set(pd[3])
            self.field5.set(pd[5])
            self.field6.set(pd[4])

            if pd[12]=="G" and (int(pd[6])>=int(wt)):

                self.field8.set(pd[6])
                self.field9.set(wt)
                self.field10.set(str(int(self.field8.get())-int(self.field9.get())))
                self.unDisable()
                self.button1.focus_set()



            elif pd[12]=="T" and (int(pd[7])<=int(wt)):
                self.field8.set(wt)
                self.field9.set(pd[7])
                self.field10.set(str(int(self.field8.get())-int(self.field9.get())))
                self.unDisable()
                self.button1.focus_set()

            else:
                result = messagebox.askquestion("GROSS WEIGHT should not be less than TARE WEIGHT", "do you want to change Gross-Tare?")
                if result == 'yes':
                    if pd[12] == "G":
                        self.field8.set(wt)
                        self.field9.set(pd[6])

                    elif pd[12] == "T":
                        self.field8.set(pd[7])
                        self.field9.set(wt)

                    self.field10.set(str(int(self.field8.get())-int(self.field9.get())))
                    self.unDisable()
                    self.button1.focus_set()




                else:
                    self.clr()
                    self.field_1.focus_set()

        elif pd[12]=="F":
            tk.messagebox.showinfo("info","FINAL WEIGHT ALREADY DONE")









    def auto_capitalize(self, variable):
        value = variable.get()
        variable.set(value.upper())


    def validate_field_6(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False




    def F2(self):
        try:
            if (self.controller.hero.get()=="<class '__main__.StartPage'>"):
                self.controller.show_frame(PageTwo)
                self.clr()
                self.field_1.focus_set()

        except:
            pass



    def asktosave(self):
        try:
            pb=db.getsecond(self.field_1.get())
            if pb[12] == "F"  :
                tk.messagebox.showinfo("Info",f"Ticket No.: {self.field_1.get()} Already Final.")

            elif pb[12] != "F"  and len(self.field_10.get())==0:
                self.gettktdetails()


            elif len(self.field_10.get())!=0:
                self.tosave()

            else:
                tk.messagebox.showerror("Error","please enter valid Ticket No.")

        except:
            tk.messagebox.showerror("Error","please enter valid Ticket No.")



    def tosave(self):

        Label_font = Font(family="Arquitecta", size=16, weight="bold")

        save_image = Image.open("res/save.jpg")
        save_photo = ImageTk.PhotoImage(save_image)

        # Load the print icon image
        print_image = Image.open("res/print.jpg")
        print_photo = ImageTk.PhotoImage(print_image)

        close_image = Image.open("res/exit.jpg")
        close_photo = ImageTk.PhotoImage(close_image)

        # Create a custom dialog window
        self.dialog = tk.Toplevel(bg="white")
        self.dialog.title("Save, Print, or Close")
        self.dialog.iconbitmap("myicon.ico")
        # Display the message
        message_label = tk.Label(self.dialog, text=" Save, Print, or Close",font=Label_font,bg="white")
        message_label.pack(padx=20, pady=10)


        save_button = tk.Button(self.dialog, image=save_photo, compound="left", command=lambda : self.save())
        save_button.image = save_photo
        save_button.bind("<Return>",lambda e:self.save())
        save_button.pack(side='left',padx=10, pady=5)



        # Create buttons with icons
        print_button = tk.Button(self.dialog, image=print_photo, compound="left",command=lambda :self.save("print"))
        print_button.image = print_photo
        print_button.bind("<Return>",lambda e:self.save("print"))
        print_button.pack(side='left',padx=10, pady=5)

        close_button = tk.Button(self.dialog, image=close_photo, command=self.dialog.destroy)
        close_button.image = close_photo
        close_button.pack(side='left',padx=10, pady=5)

        save_button.focus_set()

        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        dialog_width = 500  # Adjust the width of the dialog box as needed
        dialog_height = 200  # Adjust the height of the dialog box as needed
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


    def save(self,pp=None):
        pd=db.getsecond(self.field_1.get())
        oldGW=str(pd[6])
        oldTW=str(pd[7])
        oldGWD=pd[8]
        oldGWT=pd[9]
        oldTWD=pd[10]
        oldTWT=pd[11]
        GT=pd[12]
        pic_handler = PicHandler()
        url1 = IPcam1
        filename1 = f"camera/front/{self.field_1.get()}_2.jpg"
        url2 = IPcam2
        filename2 = f"camera/back/{self.field_1.get()}_2.jpg"

        if len(self.field_1.get())!=0:
            VehicleNo=self.field_2.get()
            VehicleType=self.field_3.get()
            PartyName=self.field_4.get()
            Charges=self.field_6.get()
            Material=self.field_5.get()
            GrossWeight=self.field_8.get()
            TareWeight=self.field_9.get()
            Final="F"

            if GT=="T" and oldTW==TareWeight :
                GrossWeightDate=self.field_01.get()
                GrossWeightTime=self.field_02.get()
                TareWeightDate=oldTWD
                TareWeightTime=oldTWT
            elif GT=="G" and oldGW==GrossWeight:
                GrossWeightDate=oldGWD
                GrossWeightTime=oldGWT
                TareWeightDate=self.field_01.get()
                TareWeightTime=self.field_02.get()

            elif GT=="T" and oldTW==GrossWeight:
                GrossWeightDate=oldTWD
                GrossWeightTime=oldTWT
                TareWeightDate=self.field_01.get()
                TareWeightTime=self.field_02.get()


            else:
                GrossWeightDate=self.field_01.get()
                GrossWeightTime=self.field_02.get()
                TareWeightDate=oldGWD
                TareWeightTime=oldGWT

            NetWeight=self.field_10.get()
            NetWeightDate=self.field_01.get()
            NetWeightTime=self.field_02.get()

            savedata=[VehicleNo,VehicleType,PartyName,Charges,
                    Material,GrossWeight,TareWeight,GrossWeightDate,
                      GrossWeightTime,TareWeightDate,TareWeightTime,Final,NetWeight,NetWeightDate,NetWeightTime,pd[0]]

            try:
                
                loop = asyncio.get_event_loop()
                loop.run_until_complete(pic_handler.download_images(url1, filename1, url2, filename2))
                db.UpdateWbData(savedata)
                tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
                if pp=="print":
                    savedata.insert(0, pd[0])
                    try:
                        zebrapl.print_ticket(savedata,"original","F")
                    except:
                        tk.messagebox.showerror("Print Error","Unable to Initialize printer.")

            except:
                tk.messagebox.showerror("error","data saving not done")

            self.close()

        else:
            tk.messagebox.showerror("ERROR_12","Ticket No. Not Valid")
            self.clr()
            self.field_1.focus_set()


        self.dialog.destroy()
        self.controller.frames[StartPage].refresh()
        self.close()







    def clr(self):
        self.field01.set(datetime.date.today().strftime("%d-%m-%Y"))
        self.field02.set(datetime.datetime.now().strftime("%H:%M:%S"))
        self.field_1.config(state="normal",disabledbackground="lightyellow")
        self.field_2.config(state="disabled",disabledbackground="lightyellow")
        self.field_3.config(state="disabled",disabledbackground="lightyellow")
        self.field_4.config(state="disabled",disabledbackground="lightyellow")
        self.field_5.config(state="disabled",disabledbackground="lightyellow")
        self.field_6.config(state="disabled",disabledbackground="lightyellow")


        self.field1.set("")
        self.field2.set("")
        self.field3.set("")
        self.field4.set("")
        self.field5.set("")
        self.field6.set("")

        self.field8.set("")
        self.field9.set("")
        self.field10.set("")




    def setweight(self):
        wt=self.controller.TempValue.get()
        if self.field7.get()=="G":
            self.field9.set(wt)
            self.field8.set("0")

        else:
            self.field8.set(wt)
            self.field9.set("0")



    def close(self):
        self.clr()
        self.controller.show_frame(StartPage)
        self.controller.focus_set()





class PageFive(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        frame2 = tk.Frame(self, bg='#FFF5EE')

        self.field01 = tk.StringVar()
        self.field02 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()
        self.field5 = tk.StringVar()
        self.field6 = tk.StringVar()
        self.field7 = tk.StringVar()
        self.field8 = tk.StringVar()
        self.field9 = tk.StringVar()
        self.field10 = tk.StringVar()

        self.controller = controller

        Label_font = Font(family="Arquitecta", size=16, weight="bold")
        field_font = Font(family="Arquitecta", size=18)
        field5font = Font(family="Arquitecta", size=32, weight="bold")
        field1font = Font(family="Arquitecta", size=25, weight="bold")



        frame2.pack(fill='both', expand=True,anchor="center")

        # Create a LabelFrame
        label_frame = tk.LabelFrame(frame2, text="Details",bg='#FFF5EE',font=Label_font)
        label_frame.grid(row=1,column=0,pady=20,ipady=10,rowspan=2,sticky="E")

        # Create Labels and corresponding Entry fields
        labels = ["Date/Time :", "Ticket No :", "Vehicle No :", "Vehicle Type :",
                  "Party Name :", "Material :", "Charges :", "F5 Final Weight","Gross Weight :", "Tare Weight :",
                  "Net Weight :"]

        self.label_0 = tk.Label(label_frame, text=labels[0], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_0.grid(row=5, column=2, padx=25, pady=0, sticky='w')
        self.field_01 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field01, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=0)
        self.field_01.grid(row=5, column=3, padx=20, pady=0, sticky='w')

        self.field_02 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field02, width=8,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=0)
        self.field_02.grid(row=5, column=4, padx=0, pady=0, sticky='w')




        self.label_1 = tk.Label(label_frame, text=labels[1], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_1.grid(row=6, column=2, padx=20, pady=0, sticky='w')
        self.field_1 = tk.Entry(label_frame, disabledforeground="red", bg='white', textvariable=self.field1, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field1font, justify='center',
                                exportselection=0)
        self.field_1.bind("<Return>", lambda e: self.field_2.focus_set())
        self.field_1.grid(row=6, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.label_2 = tk.Label(label_frame, text=labels[2], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_2.grid(row=7, column=2, padx=20, pady=0, sticky='w')
        self.field_2 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field2, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_2.bind("<Return>", lambda e: self.field_3.focus_set())
        self.field_2.grid(row=7, column=3, padx=20, pady=0, columnspan=2)

        self.label_3 = tk.Label(label_frame, text=labels[3], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_3.grid(row=8, column=2, padx=20, pady=0, sticky='w')
        self.field_3 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field3, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_3.bind("<Return>", lambda e: self.field_4.focus_set())
        self.field_3.grid(row=8, column=3, padx=20, pady=0, columnspan=2)

        self.label_4 = tk.Label(label_frame, text=labels[4], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_4.grid(row=9, column=2, padx=20, pady=0, sticky='w')
        self.field_4 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field4, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_4.bind("<Return>", lambda e: self.field_5.focus_set())
        self.field_4.grid(row=9, column=3, padx=20, pady=0, columnspan=2)

        self.label_5 = tk.Label(label_frame, text=labels[5], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_5.grid(row=10, column=2, padx=20, pady=0, sticky='w')
        self.field_5 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field5, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_5.bind("<Return>", lambda e: self.field_6.focus_set())
        self.field_5.grid(row=10, column=3, padx=20, pady=0, columnspan=2)

        self.label_6 = tk.Label(label_frame, text=labels[6], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_6.grid(row=11, column=2, padx=20, pady=0, sticky='w')
        self.field_6 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field6, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)

        self.field_6.bind("<Return>", lambda e: self.field_9.focus_set())
        self.field_6.grid(row=11, column=3, padx=20, pady=0, columnspan=2)

        self.label_7 = tk.Label(label_frame, text=labels[7], fg="grey",bg='#FFF5EE', font=field5font)
        self.label_7.grid(row=12, column=2, padx=20, pady=0,columnspan=2, sticky='w')



        label_frame1 = tk.LabelFrame(frame2, text="Weight",  bg='#FFF5EE', font=Label_font)
        label_frame1.grid(row=1, column=1,padx=50, ipady=10)

        self.label_8 = tk.Label(label_frame1, text=labels[8], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_8.grid(row=0, column=0, padx=20, pady=0, sticky='w')
        self.field_8 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field8, width=20,
                            highlightthickness=2, highlightcolor='yellow',font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=0)
        self.field_8.grid(row=0, column=1, padx=20, pady=0)

        self.label_9 = tk.Label(label_frame1, text=labels[9], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_9.grid(row=1, column=0, padx=20, pady=0, sticky='w')
        self.field_9 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field9, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,justify='center',
                            exportselection=0)
        self.field_9.bind("<Return>",lambda e:self.setweight())

        self.field_9.grid(row=1, column=1, padx=20, pady=0)

        self.label_10 = tk.Label(label_frame1, text=labels[10], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_10.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.field_10 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field10, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=0)
        self.field_10.grid(row=2, column=1, padx=20, pady=0)





        button_frame = tk.Frame(frame2, bg='#FFF5EE')
        button_frame.grid(row=2,column=1,padx=50,pady=10,sticky="nsew")

        image1 = Image.open("res/save.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/exit.jpg")
        button_image3 = ImageTk.PhotoImage(image3)



        self.button1 = tk.Button(button_frame,relief="groove", image=button_image1, compound="left",command=lambda :self.asktosave())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.asktosave())
        self.button1.grid(row=0,column=0, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=1, padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.close())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.close())
        button3.grid(row=0,column=2, padx=10, pady=10)




        self.field01.trace('w', lambda *args: self.auto_capitalize(self.field01))
        self.field02.trace('w', lambda *args: self.auto_capitalize(self.field02))
        self.field1.trace('w', lambda *args: self.auto_capitalize(self.field1))
        self.field2.trace('w', lambda *args: self.auto_capitalize(self.field2))
        self.field3.trace('w', lambda *args: self.auto_capitalize(self.field3))
        self.field4.trace('w', lambda *args: self.auto_capitalize(self.field4))
        self.field5.trace('w', lambda *args: self.auto_capitalize(self.field5))


        self.validation6=self.register(self.validate_field_6)
        self.field_6.config(validate='key',validatecommand=(self.validation6,'%P'))
        self.field_9.config(validate='key',validatecommand=(self.validation6,'%P'))


        self.setweight()


        self.controller.bind("<F5>", lambda e: self.F5())




    def auto_capitalize(self, variable):
        value = variable.get()
        variable.set(value.upper())


    def validate_field_6(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False




    def F5(self):
        try:
            if (self.controller.hero.get()=="<class '__main__.StartPage'>"):
                self.controller.show_frame(PageFive)
                self.clr()
                self.field_2.focus_set()

        except:
            pass


    def asktosave(self):
        if len(self.field_10.get())!=0:
            if float(self.field_10.get())>=0:
                self.tosave()
            else:
                tk.messagebox.showerror("Error","Tare Weight must not be greater than Gross Weight")
                self.field9.set("")
                self.field_9.focus_set()

        else:
            tk.messagebox.showerror("ERROR","PLEASE ENTER TARE WEIGHT")





    def tosave(self):
        Label_font = Font(family="Arquitecta", size=16, weight="bold")

        save_image = Image.open("res/save.jpg")
        save_photo = ImageTk.PhotoImage(save_image)

        # Load the print icon image
        print_image = Image.open("res/print.jpg")
        print_photo = ImageTk.PhotoImage(print_image)

        close_image = Image.open("res/exit.jpg")
        close_photo = ImageTk.PhotoImage(close_image)

        # Create a custom dialog window
        self.dialog = tk.Toplevel(bg="white")
        self.dialog.title("Save, Print, or Close")
        self.dialog.iconbitmap("myicon.ico")
        # Display the message
        message_label = tk.Label(self.dialog, text=" Save, Print, or Close",font=Label_font,bg="white")
        message_label.pack(padx=20, pady=10)


        save_button = tk.Button(self.dialog, image=save_photo, compound="left", command=lambda : self.save())
        save_button.image = save_photo
        save_button.bind("<Return>",lambda e:self.save())
        save_button.pack(side='left',padx=10, pady=5)



        # Create buttons with icons
        print_button = tk.Button(self.dialog, image=print_photo, compound="left",command=lambda :self.save("print"))
        print_button.image = print_photo
        print_button.bind("<Return>",lambda e:self.save("print"))
        print_button.pack(side='left',padx=10, pady=5)

        close_button = tk.Button(self.dialog, image=close_photo, command=self.dialog.destroy)
        close_button.image = close_photo
        close_button.bind("<Return>",lambda e:self.dialog.destroy)
        close_button.pack(side='left',padx=10, pady=5)

        print_button.focus_set()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        dialog_width = 500  # Adjust the width of the dialog box as needed
        dialog_height = 200  # Adjust the height of the dialog box as needed
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")





    def save(self,pp=None):

        VehicleNo=self.field_2.get()
        VehicleType=self.field_3.get()
        PartyName=self.field_4.get()
        Charges=self.field_6.get()
        Material=self.field_5.get()
        GrossWeight=self.field_8.get()
        TareWeight=self.field_9.get()
        GrossWeightDate=self.field_01.get()
        GrossWeightTime=self.field_02.get()
        TareWeightDate=self.field_01.get()
        TareWeightTime=self.field_02.get()

        Final="F"
        NetWeight=self.field_10.get()
        NetWeightDate=self.field_01.get()
        NetWeightTime=self.field_02.get()
        pic_handler = PicHandler()
        url1 = IPcam1
        filename1 = f"camera/front/{self.field_1.get()}_1.jpg"
        url2 = IPcam2
        filename2 = f"camera/back/{self.field_1.get()}_1.jpg"



        savedata=[VehicleNo,VehicleType,PartyName,Charges,
                Material,GrossWeight,TareWeight,GrossWeightDate,
                  GrossWeightTime,TareWeightDate,TareWeightTime,Final,NetWeight,NetWeightDate,NetWeightTime]


        try:

            db.SaveWbData(savedata)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(pic_handler.download_images(url1, filename1, url2, filename2))
            tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
            if pp=="print":
                savedata.insert(0, self.field_1.get())
                try:
                    zebrapl.print_ticket(savedata,"original","F")
                except:
                    tk.messagebox.showerror("Print Error","Unable to Initialize printer.")

        except:
            tk.messagebox.showerror("error","data saving not done")


        tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
        self.dialog.destroy()
        self.controller.frames[StartPage].refresh()
        self.close()





    def clr(self):
        self.field01.set(datetime.date.today().strftime("%d-%m-%Y"))
        self.field02.set(datetime.datetime.now().strftime("%H:%M:%S"))
        rst=db.lastRst()
        if rst==None:
            self.field1.set("1")
        else:
            self.field1.set(rst+1)

        self.field2.set("")
        self.field3.set("")
        self.field4.set("")
        self.field5.set("")
        self.field6.set("")
        self.field7.set("")
        self.field8.set("")
        self.field9.set("")
        self.field10.set("")
        self.field_9.config(state="normal")



    def setweight(self):
        wt=self.controller.TempValue.get()
        self.field8.set(wt)

        if len(self.field9.get())!=0:
            if int(self.field8.get())>=int(self.field9.get()) :
                nwt=int(self.field8.get())-int(self.field9.get())
                self.field10.set(nwt)
                self.field_9.config(state="disabled")
                self.button1.focus_set()
        else:
            self.field10.set("")
            self.field8.set("")



    def close(self):
        self.clr()
        self.controller.show_frame(StartPage)
        self.controller.focus_set()




class PageManual(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        frame2 = tk.Frame(self, bg='#FFF5EE')

        self.field01 = tk.StringVar()
        self.field02 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()
        self.field5 = tk.StringVar()
        self.field6 = tk.StringVar()
        self.field7 = tk.StringVar()
        self.field8 = tk.StringVar()
        self.field9 = tk.StringVar()
        self.field10 = tk.StringVar()

        self.controller = controller

        Label_font = Font(family="Arquitecta", size=16, weight="bold")
        field_font = Font(family="Arquitecta", size=18)
        field5font = Font(family="Arquitecta", size=32, weight="bold")
        field1font = Font(family="Arquitecta", size=25, weight="bold")



        frame2.pack(fill='both', expand=True,anchor="center")

        # Create a LabelFrame
        label_frame = tk.LabelFrame(frame2, text="Details",bg='#FFF5EE',font=Label_font)
        label_frame.grid(row=1,column=0,pady=20,ipady=10,rowspan=2,sticky="E")

        # Create Labels and corresponding Entry fields
        labels = ["Date/Time :", "Ticket No :", "Vehicle No :", "Vehicle Type :",
                  "Party Name :", "Material :", "Charges :", "F5_ Final Weight","Gross Weight :", "Tare Weight :",
                  "Net Weight :"]

        self.label_0 = tk.Label(label_frame, text=labels[0], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_0.grid(row=5, column=2, padx=25, pady=0, sticky='w')
        self.field_01 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field01, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=0)
        self.field_01.grid(row=5, column=3, padx=20, pady=0, sticky='w')

        self.field_02 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field02, width=8,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=0)
        self.field_02.grid(row=5, column=4, padx=0, pady=0, sticky='w')




        self.label_1 = tk.Label(label_frame, text=labels[1], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_1.grid(row=6, column=2, padx=20, pady=0, sticky='w')
        self.field_1 = tk.Entry(label_frame, disabledforeground="red", bg='white', textvariable=self.field1, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field1font, justify='center',
                                exportselection=0)
        self.field_1.bind("<Return>", lambda e: self.field_2.focus_set())
        self.field_1.grid(row=6, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.label_2 = tk.Label(label_frame, text=labels[2], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_2.grid(row=7, column=2, padx=20, pady=0, sticky='w')
        self.field_2 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field2, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_2.bind("<Return>", lambda e: self.field_3.focus_set())
        self.field_2.grid(row=7, column=3, padx=20, pady=0, columnspan=2)

        self.label_3 = tk.Label(label_frame, text=labels[3], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_3.grid(row=8, column=2, padx=20, pady=0, sticky='w')
        self.field_3 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field3, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_3.bind("<Return>", lambda e: self.field_4.focus_set())
        self.field_3.grid(row=8, column=3, padx=20, pady=0, columnspan=2)

        self.label_4 = tk.Label(label_frame, text=labels[4], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_4.grid(row=9, column=2, padx=20, pady=0, sticky='w')
        self.field_4 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field4, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_4.bind("<Return>", lambda e: self.field_5.focus_set())
        self.field_4.grid(row=9, column=3, padx=20, pady=0, columnspan=2)

        self.label_5 = tk.Label(label_frame, text=labels[5], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_5.grid(row=10, column=2, padx=20, pady=0, sticky='w')
        self.field_5 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field5, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)
        self.field_5.bind("<Return>", lambda e: self.field_6.focus_set())
        self.field_5.grid(row=10, column=3, padx=20, pady=0, columnspan=2)

        self.label_6 = tk.Label(label_frame, text=labels[6], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_6.grid(row=11, column=2, padx=20, pady=0, sticky='w')
        self.field_6 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field6, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font, justify='center',
                                exportselection=0)

        self.field_6.bind("<Return>", lambda e: self.field_8.focus_set())
        self.field_6.grid(row=11, column=3, padx=20, pady=0, columnspan=2)

        self.label_7 = tk.Label(label_frame, text=labels[7], fg="grey",bg='#FFF5EE', font=field5font)
        self.label_7.grid(row=12, column=2, padx=20, pady=0,columnspan=2, sticky='w')



        label_frame1 = tk.LabelFrame(frame2, text="Weight",  bg='#FFF5EE', font=Label_font)
        label_frame1.grid(row=1, column=1,padx=50, ipady=10)

        self.label_8 = tk.Label(label_frame1, text=labels[8], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_8.grid(row=0, column=0, padx=20, pady=0, sticky='w')
        self.field_8 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field8, width=20,
                            highlightthickness=2, highlightcolor='yellow',font=field1font,disabledforeground="blue",
                            disabledbackground="lightyellow", justify='center',
                            exportselection=0)
        
        self.field_8.bind("<Return>",lambda e:self.field_9.focus_set())

        self.field_8.grid(row=0, column=1, padx=20, pady=0)

        self.label_9 = tk.Label(label_frame1, text=labels[9], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_9.grid(row=1, column=0, padx=20, pady=0, sticky='w')
        self.field_9 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field9, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,justify='center',
                            exportselection=0)
        self.field_9.bind("<Return>",lambda e:self.setweight())

        self.field_9.grid(row=1, column=1, padx=20, pady=0)

        self.label_10 = tk.Label(label_frame1, text=labels[10], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_10.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.field_10 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field10, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=0)
        self.field_10.grid(row=2, column=1, padx=20, pady=0)





        button_frame = tk.Frame(frame2, bg='#FFF5EE')
        button_frame.grid(row=2,column=1,padx=50,pady=10,sticky="nsew")

        image1 = Image.open("res/save.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/exit.jpg")
        button_image3 = ImageTk.PhotoImage(image3)



        self.button1 = tk.Button(button_frame,relief="groove", image=button_image1, compound="left",command=lambda :self.asktosave())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.asktosave())
        self.button1.grid(row=0,column=0, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=1, padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.close())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.close())
        button3.grid(row=0,column=2, padx=10, pady=10)




        self.field01.trace('w', lambda *args: self.auto_capitalize(self.field01))
        self.field02.trace('w', lambda *args: self.auto_capitalize(self.field02))
        self.field1.trace('w', lambda *args: self.auto_capitalize(self.field1))
        self.field2.trace('w', lambda *args: self.auto_capitalize(self.field2))
        self.field3.trace('w', lambda *args: self.auto_capitalize(self.field3))
        self.field4.trace('w', lambda *args: self.auto_capitalize(self.field4))
        self.field5.trace('w', lambda *args: self.auto_capitalize(self.field5))


        self.validation6=self.register(self.validate_field_6)
        self.field_6.config(validate='key',validatecommand=(self.validation6,'%P'))
        self.field_9.config(validate='key',validatecommand=(self.validation6,'%P'))
        self.field_8.config(validate='key',validatecommand=(self.validation6,'%P'))



        self.setweight()


        self.controller.bind("<Alt_L>"+"<m>", lambda e: self.FM())




    def auto_capitalize(self, variable):
        value = variable.get()
        variable.set(value.upper())


    def validate_field_6(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False




    def FM(self):
        try:
            if (self.controller.hero.get()=="<class '__main__.StartPage'>"):
                self.controller.show_frame(PageManual)
                self.clr()
                self.field_2.focus_set()

        except:
            pass


    def asktosave(self):
        if len(self.field_10.get())!=0:
            if float(self.field_10.get())>=0:
                self.tosave()
            else:
                tk.messagebox.showerror("Error","Tare Weight must not be greater than Gross Weight")
                self.field9.set("")
                self.field_9.focus_set()

        else:
            tk.messagebox.showerror("ERROR","PLEASE ENTER TARE WEIGHT")





    def tosave(self):
        Label_font = Font(family="Arquitecta", size=16, weight="bold")

        save_image = Image.open("res/save.jpg")
        save_photo = ImageTk.PhotoImage(save_image)

        # Load the print icon image
        print_image = Image.open("res/print.jpg")
        print_photo = ImageTk.PhotoImage(print_image)

        close_image = Image.open("res/exit.jpg")
        close_photo = ImageTk.PhotoImage(close_image)

        # Create a custom dialog window
        self.dialog = tk.Toplevel(bg="white")
        self.dialog.title("Save, Print, or Close")
        self.dialog.iconbitmap("myicon.ico")
        # Display the message
        message_label = tk.Label(self.dialog, text=" Save, Print, or Close",font=Label_font,bg="white")
        message_label.pack(padx=20, pady=10)


        save_button = tk.Button(self.dialog, image=save_photo, compound="left", command=lambda : self.save())
        save_button.image = save_photo
        save_button.bind("<Return>",lambda e:self.save())
        save_button.pack(side='left',padx=10, pady=5)



        # Create buttons with icons
        print_button = tk.Button(self.dialog, image=print_photo, compound="left",command=lambda :self.save("print"))
        print_button.image = print_photo
        print_button.bind("<Return>",lambda e:self.save("print"))
        print_button.pack(side='left',padx=10, pady=5)

        close_button = tk.Button(self.dialog, image=close_photo, command=self.dialog.destroy)
        close_button.image = close_photo
        close_button.bind("<Return>",lambda e:self.dialog.destroy)
        close_button.pack(side='left',padx=10, pady=5)

        print_button.focus_set()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        dialog_width = 500  # Adjust the width of the dialog box as needed
        dialog_height = 200  # Adjust the height of the dialog box as needed
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")





    def save(self,pp=None):

        VehicleNo=self.field_2.get()
        VehicleType=self.field_3.get()
        PartyName=self.field_4.get()
        Charges=self.field_6.get()
        Material=self.field_5.get()
        GrossWeight=self.field_8.get()
        TareWeight=self.field_9.get()
        GrossWeightDate=self.field_01.get()
        GrossWeightTime=self.field_02.get()
        TareWeightDate=self.field_01.get()
        TareWeightTime=self.field_02.get()

        Final="F"
        NetWeight=self.field_10.get()
        NetWeightDate=self.field_01.get()
        NetWeightTime=self.field_02.get()
        pic_handler = PicHandler()
        url1 = IPcam1
        filename1 = f"camera/front/{self.field_1.get()}_1.jpg"
        url2 = IPcam2
        filename2 = f"camera/back/{self.field_1.get()}_1.jpg"




        savedata=[VehicleNo,VehicleType,PartyName,Charges,
                Material,GrossWeight,TareWeight,GrossWeightDate,
                  GrossWeightTime,TareWeightDate,TareWeightTime,Final,NetWeight,NetWeightDate,NetWeightTime]


        try:
            db.SaveWbData(savedata)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(pic_handler.download_images(url1, filename1, url2, filename2))
            

            tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
            if pp=="print":
                savedata.insert(0, self.field_1.get())
                try:
                    zebrapl.print_ticket(savedata,"original","F")
                except:
                    tk.messagebox.showerror("Print Error","Unable to Initialize printer.")

        except:
            tk.messagebox.showerror("error","data saving not done")


        tk.messagebox.showinfo("DONE",f"TICKET No {self.field1.get()} SAVED SUCCESSFULLY")
        self.dialog.destroy()
        self.controller.frames[StartPage].refresh()
        self.close()





    def clr(self):
        self.field01.set(datetime.date.today().strftime("%d-%m-%Y"))
        self.field02.set(datetime.datetime.now().strftime("%H:%M:%S"))
        rst=db.lastRst()
        if rst==None:
            self.field1.set("1")
        else:
            self.field1.set(rst+1)

        self.field2.set("")
        self.field3.set("")
        self.field4.set("")
        self.field5.set("")
        self.field6.set("")
        self.field7.set("")
        self.field8.set("")
        self.field9.set("")
        self.field10.set("")
        self.field_8.config(state="normal")
        self.field_9.config(state="normal")



    def setweight(self):

        if len(self.field9.get())!=0:
            if int(self.field8.get())>=int(self.field9.get()) :
                nwt=int(self.field8.get())-int(self.field9.get())
                self.field10.set(nwt)
                self.field_8.config(state="disabled")
                self.field_9.config(state="disabled")
                self.button1.focus_set()
        else:
            self.field10.set("")
            self.field8.set("")



    def close(self):
        self.clr()
        self.controller.show_frame(StartPage)
        self.controller.focus_set()








class Report(tk.Toplevel):

    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent,**kwargs,bg="#ADD8E0")



        self.geometry(str(self.winfo_screenwidth())+"x"+str(self.winfo_screenheight()))
        self.state('zoomed')
        self.iconbitmap('myicon.ico')
        self.focus_set()
        self.title("REPORTS")


        label_font = Font(family="Arquitecta", size=14)
        field_font = Font(family="Arquitecta", size=12)
        l_font = Font(family="Arquitecta", size=60)

        frame_but = tk.Frame(self, bg="#ADD8E0")
        frame_but.pack(fill="both", expand=True, padx=30, pady=10,anchor="e")

        frame_top = tk.Frame(self, bg="white")
        frame_top.pack(fill="both", expand=True, padx=10, pady=10)

        botom_frame=tk.Frame(self,bg="#ADD8E0")
        botom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        start_ticket_label = tk.Label(frame_but,font=label_font, text="Start Ticket No : ", bg="#ADD8E0")
        start_ticket_label.grid(row=2, column=0, sticky="w")

        self.start_ticket_var = tk.StringVar()
        self.start_ticket_entry = ttk.Entry(frame_but,font=field_font, textvariable=self.start_ticket_var, validate="key")
        self.start_ticket_entry['validatecommand'] = (self.start_ticket_entry.register(self.validate_positive_int), '%P')
        self.start_ticket_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        end_ticket_label = tk.Label(frame_but,font=label_font, text="End Ticket No : ", bg="#ADD8E0")
        end_ticket_label.grid(row=3, column=0, sticky="w")

        self.end_ticket_var = tk.StringVar()
        self.end_ticket_entry = ttk.Entry(frame_but,font=field_font, textvariable=self.end_ticket_var, validate="key")
        self.end_ticket_entry['validatecommand'] = (self.end_ticket_entry.register(self.validate_positive_int), '%P')
        self.end_ticket_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")



        start_date_label = tk.Label(frame_but,font=label_font, text="Start Date : ", bg="#ADD8E0")
        start_date_label.grid(row=2, column=2, sticky="w")

        self.start_date_entry = DateEntry(frame_but,font=field_font,state="readonly",background="darkblue",
                                          foreground="white", date_pattern="dd-mm-yyyy", borderwidth=2)
        self.start_date_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # Add the End Date label and DateEntry
        end_date_label = tk.Label(frame_but,font=label_font, text="End Date : ", bg="#ADD8E0")
        end_date_label.grid(row=3, column=2, sticky="w")

        self.end_date_entry = DateEntry(frame_but,font=field_font, background="darkblue",state="readonly", date_pattern="dd-mm-yyyy",
                                        foreground="white", borderwidth=2)
        self.end_date_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")



        vehicle_no_label = tk.Label(frame_but,font=label_font, text="Vehicle No : ", bg="#ADD8E0")
        vehicle_no_label.grid(row=2, column=4, sticky="w")


        self.vehicle_no_var = tk.StringVar()
        self.vehicle_no_entry = ttk.Entry(frame_but,font=field_font, textvariable=self.vehicle_no_var)
        self.vehicle_no_entry.grid(row=2, column=5, padx=5, pady=5, sticky="w")

        party_name_label = tk.Label(frame_but,font=label_font, text="Party Name : ", bg="#ADD8E0")
        party_name_label.grid(row=3, column=4, sticky="w")

        self.party_name_var = tk.StringVar()
        self.party_name_entry = ttk.Entry(frame_but,font=field_font, textvariable=self.party_name_var)
        self.party_name_entry.grid(row=3, column=5, padx=5, pady=5, sticky="w")

        material_label = tk.Label(frame_but,font=label_font, text="Material : ", bg="#ADD8E0")
        material_label.grid(row=2, column=6, sticky="w")

        self.material_var = tk.StringVar()
        self.material_entry = ttk.Entry(frame_but,font=field_font, textvariable=self.material_var)
        self.material_entry.grid(row=2, column=7, padx=5, pady=5, sticky="w")

        vehicle_type_label = tk.Label(frame_but,font=label_font, text="Vehicle Type : ", bg="#ADD8E0")
        vehicle_type_label.grid(row=3, column=6, sticky="w")


        self.vehicle_type_var = tk.StringVar()
        self.vehicle_type_entry = ttk.Entry(frame_but,font=field_font,textvariable=self.vehicle_type_var)
        self.vehicle_type_entry.grid(row=3, column=7, padx=5, pady=5, sticky="w")

        Report_label = tk.Label(frame_but,font=l_font, text="Report", bg="#ADD8E0")
        Report_label.grid(row=0, column=0,rowspan=2,columnspan=5,padx=20)

        F_label = tk.Label(frame_but,font=label_font, text="Ticket Type :", bg="#ADD8E0")
        F_label.grid(row=0, column=5,pady=10,padx=10,sticky="e")

        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(frame_but, textvariable=self.combobox_var,font=field_font,width=8, values=["FINAL", "ALL","PENDING"], state="readonly")
        self.combobox.grid(row=0, column=6,sticky="w", padx=10, pady=10)



        sql_data=db.GetAll()
        self.df = pd.DataFrame(sql_data)



        treeview_width = int((self.winfo_screenwidth())/1.6)


        self.treeview = ttk.Treeview(frame_top, columns=("TicketNo",
            "VehicleNo", "VehicleType", "PartyName", "Charges", "Material",
            "GrossWeight", "TareWeight", "GrossWeightDate", "GrossWeightTime",
            "TareWeightDate", "TareWeightTime","GrossTareFinal","NetWeight","NetWeightDate","NetWeightTime"
        ))
        self.treeview.column("#0", minwidth=0, width=0, stretch=False, anchor="center")

        self.treeview.column("TicketNo", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("VehicleNo", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("VehicleType", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("PartyName", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("Charges", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("Material", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeight", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeight", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeightDate", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossWeightTime", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeightDate", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("TareWeightTime", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("GrossTareFinal", minwidth=int(treeview_width * 0.1), width=int(treeview_width * 0.1), stretch=False, anchor="center")
        self.treeview.column("NetWeight", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("NetWeightDate", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")
        self.treeview.column("NetWeightTime", minwidth=int(treeview_width * 0.2), width=int(treeview_width * 0.2), stretch=False, anchor="center")

        # Add headings
        self.treeview.heading("TicketNo", text="Ticket No.")
        self.treeview.heading("VehicleNo", text="Vehicle No.")
        self.treeview.heading("VehicleType", text="Vehicle Type")
        self.treeview.heading("PartyName", text="Party Name")
        self.treeview.heading("Charges", text="Charges")
        self.treeview.heading("Material", text="Material")
        self.treeview.heading("GrossWeight", text="Gross Weight")
        self.treeview.heading("TareWeight", text="Tare Weight")
        self.treeview.heading("GrossWeightDate", text="Gross Weight Date")
        self.treeview.heading("GrossWeightTime", text="Gross Weight Time")
        self.treeview.heading("TareWeightDate", text="Tare Weight Date")
        self.treeview.heading("TareWeightTime", text="Tare Weight Time")
        self.treeview.heading("GrossTareFinal", text="G/T/F")
        self.treeview.heading("NetWeight", text="Net Weight")
        self.treeview.heading("NetWeightDate", text="Net Weight Date")
        self.treeview.heading("NetWeightTime", text="Net Weight Time")


        # Set the focus on the first cell of the second column
        self.treeview.focus_set()


        vsb = ttk.Scrollbar(frame_top, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Create the horizontal scrollbar
        scrollbar_x = ttk.Scrollbar(frame_top, orient="horizontal", command=self.treeview.xview)
        scrollbar_x.pack(side="bottom",fill="x")
        self.treeview.configure(xscrollcommand=scrollbar_x.set)


        self.treeview.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        Label_font = Font(family="Arquitecta", size=14)


        label_frame=tk.LabelFrame(botom_frame,bg="#ADD8E0")
        label_frame.pack(side="left")

        self.label1=tk.StringVar()
        self.label2=tk.StringVar()
        self.label3=tk.StringVar()
        self.label_1=tk.Label(label_frame,textvariable=self.label1,font=Label_font,bg="#ADD8E0")
        self.label_1.grid(row=0,column=0,sticky="w")
        self.label_2=tk.Label(label_frame,textvariable=self.label2,font=Label_font,bg="#ADD8E0")
        self.label_2.grid(row=1,column=0,sticky="w")
        self.label_3=tk.Label(label_frame,textvariable=self.label3,font=Label_font,bg="#ADD8E0")
        self.label_3.grid(row=2,column=0,sticky="w")

        self.vehicle_no_var.trace('w', lambda *args: self.auto_capitalize(self.vehicle_no_var))
        self.party_name_var.trace('w', lambda *args: self.auto_capitalize(self.party_name_var))
        self.material_var.trace('w', lambda *args: self.auto_capitalize(self.material_var))
        self.vehicle_type_var.trace('w', lambda *args: self.auto_capitalize(self.vehicle_type_var))


        # -------------------------button---------------------------

        button_frame=tk.Frame(botom_frame,bg="#ADD8E0")
        button_frame.pack(side="right")

        image1 = Image.open("res/view.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)


        image3 = Image.open("res/print.jpg")
        button_image3 = ImageTk.PhotoImage(image3)

        image4 = Image.open("res/exit.jpg")
        button_image4 = ImageTk.PhotoImage(image4)



        self.button1 = tk.Button(frame_but,relief="groove", image=button_image1, compound="left",command=lambda :self.view_report())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.view_report())
        self.button1.grid(row=0,column=7, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=3,rowspan=3,padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.printing())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.printing())
        button3.grid(row=0,column=4,rowspan=3, padx=10, pady=10)


        button4 = tk.Button(button_frame,relief="groove", image=button_image4, compound="left",command=lambda:self.close())
        button4.image = button_image4  # Store the image reference
        button4.bind("<Return>", lambda e: self.close())
        button4.grid(row=0,column=5,rowspan=3, padx=10, pady=10)



        self.delete_button = tk.Button(button_frame, text="Delete", command=lambda:self.delete_selected_record())
        self.delete_button.grid(row=0,column=1,rowspan=3, padx=10, pady=10)
        self.delete_button.grid_remove()  # Hide the button initially



        self.bind("<Alt_L>"+"<E>",lambda e:self.toggle_buttons_visibility())
        self.bind("<Alt_L>"+"<e>",lambda e:self.toggle_buttons_visibility())




        self.clr()
        self.refresh_data(self.df)

    def toggle_buttons_visibility(self):
        if self.delete_button.winfo_viewable():    
            self.delete_button.grid_remove()
        else:     
            self.delete_button.grid()

  

    def delete_selected_record(self):
        selected_item = self.treeview.focus() 
        values = self.treeview.item(selected_item, "values")
        MsgBox = tk.messagebox.askquestion ('Are You Sure','Do you want to delete '+"rst no.:"+str(values[0])+"\nrecord:"+str(values),icon = 'question')
        if MsgBox == 'yes':
            db.delone(values[0])
            MsgBox = tk.messagebox.showinfo("Done","rst no.:"+str(values[0])+"data deleted")
            self.df.drop(self.df[self.df[0] == int(values[0])].index, inplace=True)
            self.refresh_data(self.df)
            
        else:
            pass
        



    def validate_positive_int(self, value):
        if value.isdigit() or value == "":
            return True
        return False


    def auto_capitalize(self, variable):
        value = variable.get()
        variable.set(value.upper())



    def refresh_data(self,data):

        self.treeview.delete(*self.treeview.get_children())

        # Fetch data from the database
        for index, row in data.iterrows():
            values = [str(value) for value in row]
            self.treeview.insert("", index, text=index, values=values)


        sum_sno = data.index.size
        sum_netweight = pd.to_numeric(data[13], errors='coerce').astype('Int64').sum()
        sum_charges= pd.to_numeric(data[4], errors='coerce').astype('Int64').sum()
        self.label1.set(f"Total Tickets        :   {sum_sno}")
        self.label2.set(f"Total Net Weight :   {int(sum_netweight)} KG")
        self.label3.set(f"Total Charges     :   Rs {int(sum_charges)} /-")






    def close(self):
        self.clr()
        self.destroy()


    def clr(self):
        # Clear all entry box values
        self.start_ticket_var.set('')
        self.end_ticket_var.set('')

        self.start_date_entry.set_date('01-04-2023')

        # Set the end date to the current date
        current_date = datetime.datetime.now()
        current_date_str = current_date.strftime("%d-%m-%Y")
        self.end_date_entry.set_date(current_date_str)

        self.vehicle_no_var.set('')
        self.party_name_var.set('')
        self.material_var.set('')
        self.vehicle_type_var.set('')
        self.delete_button.grid_remove()
        # Set the combobox value to "ALL"
        self.combobox_var.set('ALL')

        # Call the view_report function to update the treeview based on the cleared values
        self.view_report()


    def view_report(self):
        # Get the values from the entry boxes and combo box
        start_ticket = self.start_ticket_var.get()
        end_ticket = self.end_ticket_var.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        vehicle_no = self.vehicle_no_var.get()
        party_name = self.party_name_var.get()
        material = self.material_var.get()
        vehicle_type = self.vehicle_type_var.get()
        ticket_type = self.combobox_var.get()

        # Check if the start date is less than the current date
        current_date = datetime.datetime.now().date()
        start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y").date()
        start_date_str = datetime.datetime.strptime(start_date_str, "%d-%m-%Y").date() if start_date_str else None
        end_date_str = datetime.datetime.strptime(end_date_str, "%d-%m-%Y").date() if end_date_str else None




        if start_date <= current_date:
            # Start date is before the current date, proceed with filtering
            filtered_data = self.df.copy()


            def populate_column(row):
                if row[14]:
                    return row[14]
                elif row[8]:
                    return row[8]
                else:
                    return row[10]

            # Apply the custom function to create the fourth column
            filtered_data[16] = filtered_data.apply(populate_column, axis=1)





            if ticket_type == "FINAL":
                filtered_data = filtered_data[filtered_data[12] == "F"]
            elif ticket_type == "PENDING":
                filtered_data = filtered_data[filtered_data[12] != "F"]

            if start_ticket:
                filtered_data = filtered_data[filtered_data[0] >= int(start_ticket)]

            if end_ticket:
                filtered_data = filtered_data[filtered_data[0] <= int(end_ticket)]


            filtered_data[16] = pd.to_datetime(filtered_data[16], errors="coerce",dayfirst=True).dt.date




            if start_date_str:
                filtered_data = filtered_data[(filtered_data[16] >= start_date_str)]


            if end_date_str:
                filtered_data = filtered_data[(filtered_data[16] <= end_date_str)]

            if vehicle_no:
                filtered_data = filtered_data[filtered_data[1].str.contains(vehicle_no, case=False, na=False)]

            if party_name:
                filtered_data = filtered_data[filtered_data[3].str.contains(party_name, case=False, na=False)]

            if material:
                filtered_data = filtered_data[filtered_data[5].str.contains(material, case=False, na=False)]

            if vehicle_type:
                filtered_data = filtered_data[filtered_data[2].str.contains(vehicle_type, case=False, na=False)]


            self.refresh_data(filtered_data)
        else:
            self.clr()
            tk.messagebox.showerror("ERROR","Start Date Must Be Less Than End Date")
            self.refresh_data(self.df)



    def printing(self):
        data = []
        for item_id in self.treeview.get_children():
            item_data = self.treeview.item(item_id)['values']
            data.append(item_data)


        report2.generate_pdf_report(data,self.label1.get(),self.label2.get(),self.label3.get())
        self.print_pdf()





    def print_pdf(self):
        filename = "report.pdf"
        subprocess.run(["start",filename], shell=True)

class MultiTabWindow(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)

        xcord = (self.winfo_screenwidth() / 4)
        ycord = (self.winfo_screenheight() / 4)
        window_width = int((self.winfo_screenwidth() / 2))
        window_height = int((self.winfo_screenheight() / 2))
        self.geometry(f"{window_width}x{window_height}+{int(xcord)}+{int(ycord)}")

        self.iconbitmap('myicon.ico')
        self.focus_set()
        self.title("Setting")
        self.create_tabs()
        self.frame=tk.Frame(self)
        self.frame.pack(side="bottom")
        self.save_but=tk.Button(self.frame,relief="groove",text="SAVE",font={"Arial"},bg="white",command=lambda :self.save())
        self.save_but.pack(pady=10)

    def create_tabs(self):
        # Create a tab control widget
        tab_control = ttk.Notebook(self)

        # Create multiple tabs
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab4 = ttk.Frame(tab_control)

        # Add tabs to the tab control widget
        tab_control.add(tab1, text="Company Details")
        tab_control.add(tab2, text="Printing")
        tab_control.add(tab3, text="Weight Indicator")
        tab_control.add(tab4, text="Camera Details")


        # Add content to each tab
        self.create_company_tab(tab1)
        self.create_printing_tab(tab2)
        self.create_weight_indicator_tab(tab3)
        self.create_camera_tab(tab4)
        self.clr()

        # Pack the tab control widget to display the tabs
        tab_control.pack(expand=1, fill="both")



    def create_printing_tab(self, tab):
        style=ttk.Style()
        style.configure("TLabelframe",background='#ADD8E0')
        style.configure("TLabelframe.Label",background='#ADD8E0')
        style.configure("TFrame",background='#ADD8E0')
        style.configure("TText",background='#ADD8E0')
        printer_type_frame = ttk.LabelFrame(tab, text="Printer Type")
        printer_type_frame.pack(padx=10, pady=10)

        lfont = Font(family="Arquitecta", size=12)
        efont = Font(family="Arquitecta", size=10)

        printers=zebrapl.get_available_printers()




        self.printer_type_var = tk.StringVar()
        self.printer_type_var.set("Dot Matrix Printer")

        dot_matrix_radio = tk.Radiobutton(printer_type_frame, text="Dot Matrix Printer",font=lfont,bg='#ADD8E0', variable=self.printer_type_var, value="Dot Matrix Printer")
        dot_matrix_radio.pack(anchor=tk.W)

        graphics_printer_radio = tk.Radiobutton(printer_type_frame, text="Graphics Printer (Laser, Inkjet, etc.)",font=lfont,bg='#ADD8E0', variable=self.printer_type_var, value="Graphics Printer")
        graphics_printer_radio.pack(anchor=tk.W)

        side_wise_frame = ttk.LabelFrame(tab, text="Side Wise Printing")
        side_wise_frame.pack(padx=10, pady=10)

        self.side_wise_var = tk.StringVar()
        self.side_wise_var.set("Enable")

        enable_radio = tk.Radiobutton(side_wise_frame, text="Enable", variable=self.side_wise_var,font=lfont,bg='#ADD8E0', value="Enable")
        enable_radio.pack(anchor=tk.W)

        disable_radio = tk.Radiobutton(side_wise_frame, text="Disable", variable=self.side_wise_var,font=lfont,bg='#ADD8E0', value="Disable")
        disable_radio.pack(anchor=tk.W)

        printer_setting_frame = ttk.LabelFrame(tab, text="Printer Setting")
        printer_setting_frame.pack(padx=10, pady=10)

        default_copy_label_f1 = tk.Label(printer_setting_frame, text="Default No. of Copy: F1",font=lfont,bg='#ADD8E0')
        default_copy_label_f1.pack(side=tk.LEFT, padx=5)

        self.validation=self.register(self.validate_numeric_input)

        self.default_copy_f1_var = tk.StringVar()
        default_copy_f1_entry = tk.Entry(printer_setting_frame, textvariable=self.default_copy_f1_var ,width=3,font=efont,validate='key',validatecommand=(self.validation,'%P'))
        default_copy_f1_entry.pack(side=tk.LEFT, padx=5)

        default_copy_label_f2 = tk.Label(printer_setting_frame, text="Default No. of Copy: F2", font=lfont, bg='#ADD8E0')
        default_copy_label_f2.pack(side=tk.LEFT, padx=5)

        self.default_copy_f2_var = tk.StringVar()
        default_copy_f2_entry = tk.Entry(printer_setting_frame, textvariable=self.default_copy_f2_var, width=3, font=efont, validate='key', validatecommand=(self.validation, '%P'))
        default_copy_f2_entry.pack(side=tk.LEFT, padx=5)

        default_printer_label = tk.Label(printer_setting_frame, text="Default Printer:",font=lfont,bg='#ADD8E0')
        default_printer_label.pack(side=tk.LEFT, padx=5)

        self.default_printer_var = tk.StringVar()
        default_printer_combobox = ttk.Combobox(printer_setting_frame,font=efont, textvariable=self.default_printer_var, state="readonly", values=printers)
        default_printer_combobox.pack(side=tk.LEFT, padx=5)


    def create_weight_indicator_tab(self, tab):
        style=ttk.Style()
        style.configure("TLabelframe",background='#ADD8E0')
        style.configure("TLabelframe.Label",background='#ADD8E0')
        style.configure("TFrame",background='#ADD8E0')
        style.configure("TText",background='#ADD8E0')

        frame2 = ttk.LabelFrame(tab, text="Hardware Setting")
        frame2.pack(padx=10, pady=10)


        Label1_font = ("Arial", 10)
        field_font = ("Arial", 10)

        self.field0 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()

        self.field_0_label = tk.Label(frame2, text="COM PORT :", fg="black", bg='#ADD8E0', font=Label1_font,
                                      height=1)
        self.field_0_label.grid(row=2, column=0, padx=0, pady=0, sticky='w')

        self.feild_0_value = tk.Spinbox(frame2, readonlybackground='white', textvariable=self.field0, font=field_font, state='readonly', exportselection=0)
        self.feild_0_value["values"] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10','COM11','COM12','COM13','COM14','COM15','COM16')
        self.feild_0_value.bind("<Return>", lambda e: self.feild_1_value.focus_set())
        self.feild_0_value.grid(row=2, column=1, padx=5, pady=2, columnspan=3, sticky='w')

        self.field_1_label = tk.Label(frame2, text="BAUD RATE :", fg="black",bg='#ADD8E0', font=Label1_font, height=1)
        self.field_1_label.grid(row=4, column=0, padx=0, pady=0, sticky='w')

        self.feild_1_value = tk.Spinbox(frame2, readonlybackground='white', textvariable=self.field1, font=field_font, state='readonly', exportselection=0)
        self.feild_1_value["values"] = ('600', '1200', '2400', '4800', '9600', '19200', '38400', '76800', '153600')
        self.feild_1_value.bind("<Return>", lambda e: self.feild_2_value.focus_set())
        self.feild_1_value.grid(row=4, column=1, padx=1, pady=0, columnspan=2)

        self.field_2_label = tk.Label(frame2, text="Ending String :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_2_label.grid(row=6, column=0, padx=0, pady=0, sticky='w')

        self.feild_2_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.field2, font=field_font, justify='center', exportselection=0)
        self.feild_2_value.bind("<Return>", lambda e: self.feild_3_value.focus_set())
        self.feild_2_value.grid(row=6, column=1, padx=1, pady=0, columnspan=2)

        self.field_3_label = tk.Label(frame2, text="Weighing Digits :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_3_label.grid(row=8, column=0, padx=0, pady=0, sticky='w')

        self.feild_3_value = tk.Spinbox(frame2, readonlybackground='white', textvariable=self.field3, font=field_font, state='readonly', exportselection=0)
        self.feild_3_value["values"] = ('0','1', '2', '3', '4', '5','6','7','8','9')
        self.feild_3_value.grid(row=8, column=1, padx=1, pady=0, columnspan=2)

        self.field_4_label = tk.Label(frame2, text="Rshift Digits :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_4_label.grid(row=9, column=0, padx=0, pady=0, sticky='w')

        self.feild_4_value = tk.Spinbox(frame2, readonlybackground='white', textvariable=self.field4, font=field_font, state='readonly', exportselection=0)
        self.feild_4_value["values"] = ('0','1', '2', '3', '4', '5','6','7','8','9')
        self.feild_4_value.grid(row=9, column=1, padx=1, pady=0, columnspan=2)




    def validate_numeric_input(self, input_value):
        # Validate if the input value is numeric (integer)
        try:
            if input_value == "" or int(input_value) >= 0:
                return True
            return False
        except ValueError:
            return False


    def create_camera_tab(self, tab):
        style = ttk.Style()
        style.configure("TLabelframe", background='#ADD8E0')
        style.configure("TLabelframe.Label", background='#ADD8E0')
        style.configure("TFrame", background='#ADD8E0')
        style.configure("TText", background='#ADD8E0')
        
        # Create a frame to hold the checkbox and camera details
        camera_frame = ttk.Frame(tab, style="TLabelframe")
        camera_frame.pack(padx=10, pady=10)

        # Checkbox to enable/disable cameras
        self.camera_enabled = tk.BooleanVar()
        camera_checkbox = ttk.Checkbutton(camera_frame, text="Enable Cameras", variable=self.camera_enabled)
        camera_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.pic_enabled = tk.BooleanVar()
        pic_checkbox = ttk.Checkbutton(camera_frame, text="Enable pics", variable=self.pic_enabled)
        pic_checkbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        

        # Camera details label frame
        frame2 = ttk.LabelFrame(camera_frame, text="Camera Details")
        frame2.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        Label1_font = ("Arial", 10)
        field_font = ("Arial", 10)
        self.field_cam1 = tk.Label(frame2, text="Camera 1:", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_cam1.grid(row=0, column=0, padx=0, pady=0, sticky='w')
        self.fieldcam1 = tk.StringVar()
        self.feild_cam1_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.fieldcam1, width=50, font=field_font, justify='center', exportselection=0)
        self.feild_cam1_value.bind("<Return>", lambda e: self.feild_cam2_value.focus_set())
        self.feild_cam1_value.grid(row=0, column=1, padx=1, pady=0, columnspan=2)

        self.field_cam2 = tk.Label(frame2, text="Camera 2 :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_cam2.grid(row=1, column=0, padx=0, pady=0, sticky='w')
        self.fieldcam2 = tk.StringVar()
        self.feild_cam2_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.fieldcam2, width=50, font=field_font, justify='center', exportselection=0)
        self.feild_cam2_value.bind("<Return>", lambda e: self.feild_add2_value.focus_set())
        self.feild_cam2_value.grid(row=1, column=1, padx=1, pady=0, columnspan=2)



    def create_company_tab(self, tab):
        style=ttk.Style()
        style.configure("TLabelframe",background='#ADD8E0')
        style.configure("TLabelframe.Label",background='#ADD8E0')
        style.configure("TFrame",background='#ADD8E0')
        style.configure("TText",background='#ADD8E0')
        frame2 = ttk.LabelFrame(tab, text="Company details")
        frame2.pack(padx=10, pady=10)


        Label1_font = ("Arial", 10)
        field_font = ("Arial", 10)
        self.field_cn = tk.Label(frame2, text="Company Name :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_cn.grid(row=0, column=0, padx=0, pady=0, sticky='w')
        self.fieldcn=tk.StringVar()
        self.feild_cn_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.fieldcn,width=50, font=field_font, justify='center', exportselection=0)
        self.feild_cn_value.bind("<Return>", lambda e: self.feild_add1_value.focus_set())
        self.feild_cn_value.grid(row=0, column=1, padx=1, pady=0, columnspan=2)


        self.field_add1 = tk.Label(frame2, text="Address Line 1 :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_add1.grid(row=1, column=0, padx=0, pady=0, sticky='w')
        self.fieldadd1=tk.StringVar()
        self.feild_add1_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.fieldadd1,width=50, font=field_font, justify='center', exportselection=0)
        self.feild_add1_value.bind("<Return>", lambda e: self.feild_add2_value.focus_set())
        self.feild_add1_value.grid(row=1, column=1, padx=1, pady=0, columnspan=2)


        self.field_add2 = tk.Label(frame2, text="Address Line 2 :", fg="black", bg='#ADD8E0', font=Label1_font)
        self.field_add2.grid(row=2, column=0, padx=0, pady=0, sticky='w')
        self.fieldadd2=tk.StringVar()
        self.feild_add2_value = tk.Entry(frame2, fg="black", bg='white', textvariable=self.fieldadd2,width=50, font=field_font, justify='center', exportselection=0)
        self.feild_add2_value.grid(row=2, column=1, padx=1, pady=0, columnspan=2)

    def save(self):

        CName = self.fieldcn.get()
        Add1 = self.fieldadd1.get()
        Add2 = self.fieldadd2.get()
        PType = self.printer_type_var.get()
        SWPrint = self.side_wise_var.get()
        NCopyF1 = self.default_copy_f1_var.get()
        NCopyF2 = self.default_copy_f2_var.get()
        DPrint=self.default_printer_var.get()
        CPort = self.field0.get()
        BRate = self.field1.get()
        EString = self.field2.get()
        WDigits = self.field3.get()
        RShift=self.field4.get()
        camEN=self.camera_enabled.get()
        IPcam1=self.fieldcam1.get()
        IPcam2=self.fieldcam2.get()
        picEN=self.pic_enabled.get()

        mydata=[CName,Add1,Add2,PType,SWPrint,NCopyF1,NCopyF2,DPrint,CPort,BRate,EString,WDigits,RShift,camEN,IPcam1,IPcam2,picEN]
        db.Update_Seting(mydata)
        try:
            db.Update_Seting(mydata)
            tk.messagebox.showinfo("Done","Saved Successfully !")
        except:
            tk.messagebox.showerror('error','Data Saving Error33')


    def clr(self):
        self.fieldcn.set(CN)
        self.fieldadd1.set(A_1)
        self.fieldadd2.set(A_2)
        self.printer_type_var.set(P_T)
        self.side_wise_var.set(SWP)
        self.default_copy_f1_var.set(NCPF1)
        self.default_copy_f2_var.set(NCPF2)
        self.field0.set(com)
        self.field1.set(str(baurd))
        self.field2.set(rfind)
        self.field3.set(str(WDL))
        self.default_printer_var.set(DP)
        self.field4.set(str(rshift))
        self.camera_enabled.set(camEN)
        self.fieldcam1.set(IPcam1)
        self.fieldcam2.set(IPcam2)
        self.pic_enabled.set(picEN)



class PrintViewPage(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)

        frame2 = tk.Frame(self, bg='#FFF5EE')

        self.field01 = tk.StringVar()
        self.field02 = tk.StringVar()
        self.field1 = tk.StringVar()
        self.field2 = tk.StringVar()
        self.field3 = tk.StringVar()
        self.field4 = tk.StringVar()
        self.field5 = tk.StringVar()
        self.field6 = tk.StringVar()
        self.field7 = tk.StringVar()
        self.field8 = tk.StringVar()
        self.field9 = tk.StringVar()
        self.field10 = tk.StringVar()
        self.label07 = tk.StringVar()


        Label_font = Font(family="Arquitecta", size=16, weight="bold")
        field_font = Font(family="Arquitecta", size=18)
        field5font = Font(family="Arquitecta", size=32, weight="bold")
        field1font = Font(family="Arquitecta", size=25, weight="bold")



        frame2.pack(fill='both', expand=True,anchor="center")

        # Create a LabelFrame
        label_frame = tk.LabelFrame(frame2, text="Details",bg='#FFF5EE',font=Label_font)
        label_frame.grid(row=1,column=0,pady=20,ipady=10,rowspan=2,sticky="E")

        # Create Labels and corresponding Entry fields
        labels = ["Date/Time :", "Ticket No :", "Vehicle No :", "Vehicle Type :",
                  "Party Name :", "Material :", "Charges :", "Gross(G)/Tare(T) :","Gross Weight :", "Tare Weight :",
                  "Net Weight :"]

        self.label_0 = tk.Label(label_frame, text=labels[0], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_0.grid(row=5, column=2, padx=25, pady=0, sticky='w')
        self.field_01 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field01, width=10,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_01.grid(row=5, column=3, padx=20, pady=0, sticky='w')

        self.field_02 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field02, width=8,
                                highlightthickness=2, highlightcolor='yellow',state="disabled",disabledbackground="lightyellow", font=field_font, justify='center',
                                exportselection=False)
        self.field_02.grid(row=5, column=4, padx=0, pady=0, sticky='w')




        self.label_1 = tk.Label(label_frame, text=labels[1], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_1.grid(row=6, column=2, padx=20, pady=0, sticky='w')
        self.field_1 = tk.Entry(label_frame, disabledforeground="red", bg='white', textvariable=self.field1, width=10,
                                highlightthickness=2, highlightcolor='yellow', font=field1font, justify='center',
                                exportselection=False)
        self.field_1.bind("<Return>", lambda e: self.setweight())
        self.field_1.grid(row=6, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.label_2 = tk.Label(label_frame, text=labels[2], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_2.grid(row=7, column=2, padx=20, pady=0, sticky='w')
        self.field_2 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field2, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)
        self.field_2.grid(row=7, column=3, padx=20, pady=0, columnspan=2)

        self.label_3 = tk.Label(label_frame, text=labels[3], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_3.grid(row=8, column=2, padx=20, pady=0, sticky='w')
        self.field_3 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field3, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)

        self.field_3.grid(row=8, column=3, padx=20, pady=0, columnspan=2)

        self.label_4 = tk.Label(label_frame, text=labels[4], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_4.grid(row=9, column=2, padx=20, pady=0, sticky='w')
        self.field_4 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field4, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)
        self.field_4.grid(row=9, column=3, padx=20, pady=0, columnspan=2)

        self.label_5 = tk.Label(label_frame, text=labels[5], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_5.grid(row=10, column=2, padx=20, pady=0, sticky='w')
        self.field_5 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field5, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)
        self.field_5.grid(row=10, column=3, padx=20, pady=0, columnspan=2)

        self.label_6 = tk.Label(label_frame, text=labels[6], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_6.grid(row=11, column=2, padx=20, pady=0, sticky='w')
        self.field_6 = tk.Entry(label_frame, fg="black", bg='white', textvariable=self.field6, width=20,
                                highlightthickness=2, highlightcolor='yellow', font=field_font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)

        self.field_6.grid(row=11, column=3, padx=20, pady=0, columnspan=2)

        self.label_7 = tk.Label(label_frame, text=labels[7], fg="black",bg='#FFF5EE', font=Label_font)
        self.label_7.grid(row=12, column=2, padx=20, pady=0, sticky='w')

        frame_field7=tk.Frame(label_frame,bg="#FFF5EE")
        frame_field7.grid(row=12, column=3, padx=20, pady=0, columnspan=2,sticky='w')

        self.field_7 = tk.Entry(frame_field7, fg="black", bg='white', textvariable=self.field7, width=2,
                                highlightthickness=2, highlightcolor='yellow', font=field5font,state="disabled",disabledbackground="lightyellow", justify='center',
                                exportselection=False)
        self.field_7.bind("<Return>", lambda e: self.setweight())
        self.field_7.grid(row=0, column=0,padx=20, pady=0, sticky='w')
        self.label_07 = tk.Label(frame_field7, textvariable=self.label07, fg="black",bg='#FFF5EE', font=field5font)
        self.label_07.grid(row=0, column=1, pady=0, sticky='e')



        label_frame1 = tk.LabelFrame(frame2, text="Weight",  bg='#FFF5EE', font=Label_font)
        label_frame1.grid(row=1, column=1,padx=50, ipady=10)

        self.label_8 = tk.Label(label_frame1, text=labels[8], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_8.grid(row=0, column=0, padx=20, pady=0, sticky='w')
        self.field_8 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field8, width=20,
                            highlightthickness=2, highlightcolor='yellow',font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_8.grid(row=0, column=1, padx=20, pady=0)

        self.label_9 = tk.Label(label_frame1, text=labels[9], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_9.grid(row=1, column=0, padx=20, pady=0, sticky='w')
        self.field_9 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field9, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_9.grid(row=1, column=1, padx=20, pady=0)

        self.label_10 = tk.Label(label_frame1, text=labels[10], fg="black", bg='#FFF5EE', font=Label_font)
        self.label_10.grid(row=2, column=0, padx=20, pady=0, sticky='w')
        self.field_10 = tk.Entry(label_frame1, fg="black", bg='white', textvariable=self.field10, width=20,
                            highlightthickness=2, highlightcolor='yellow', font=field1font,disabledforeground="blue",
                            state="disabled",disabledbackground="lightyellow", justify='center',
                            exportselection=False)
        self.field_10.grid(row=2, column=1, padx=20, pady=0)


        button_frame = tk.Frame(frame2, bg='#FFF5EE')
        button_frame.grid(row=2,column=1,padx=50,pady=10,sticky="nsew")

        image1 = Image.open("res/print.jpg")
        button_image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open("res/clear.jpg")
        button_image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open("res/exit.jpg")
        button_image3 = ImageTk.PhotoImage(image3)



        self.button1 = tk.Button(button_frame,relief="groove", image=button_image1, compound="left",command=lambda :self.printing())
        self.button1.image = button_image1  # Store the image reference
        self.button1.bind("<Return>", lambda e: self.printing())
        self.button1.grid(row=0,column=0, padx=10, pady=10)

        button2 = tk.Button(button_frame,relief="groove", image=button_image2, compound="left",command=lambda:self.clr())
        button2.image = button_image2  # Store the image reference
        button2.bind("<Return>", lambda e: self.clr())
        button2.grid(row=0,column=1, padx=10, pady=10)


        button3 = tk.Button(button_frame,relief="groove", image=button_image3, compound="left",command=lambda:self.close())
        button3.image = button_image3  # Store the image reference
        button3.bind("<Return>", lambda e: self.close())
        button3.grid(row=0,column=2, padx=10, pady=10)

        self.validation1=self.register(self.validate_field_1)
        self.field_1.config(validate='key',validatecommand=(self.validation1,'%P'))

        self.clr()






    def printing(self):

        try:
            df=db.getsecond(self.field_1.get())
            zebrapl.print_ticket(df,"duplicate","F")
            self.clr()
        except:
            tk.messagebox.showerror("ERROR","Printing Error")



    def validate_field_1(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False


    def clr(self):
        self.field01.set("")
        self.field02.set("")
        self.field1.set("")
        self.field_1.config(state="normal")
        self.button1.config(state="disabled")
        self.field2.set("")
        self.field3.set("")
        self.field4.set("")
        self.field5.set("")
        self.field6.set("")
        self.field7.set("")
        self.field8.set("")
        self.field9.set("")
        self.field10.set("")
        self.label07.set("")




    def setweight(self):
        try:
            df=db.getsecond(self.field_1.get())
            if df[12]=="F":
                self.field01.set(df[14])
                self.field02.set(df[15])
                self.label07.set("Final")

            elif df[12]=="G":
                self.field01.set(df[8])
                self.field02.set(df[9])
                self.label07.set("Gross")
            elif df[12]=="T":
                self.field01.set(df[10])
                self.field02.set(df[11])
                self.label07.set("Tare")

            self.field_1.config(state="disabled")
            self.button1.config(state="normal")

            self.field2.set(df[1])
            self.field3.set(df[2])
            self.field4.set(df[3])
            self.field5.set(df[5])
            self.field6.set(df[4])
            self.field7.set(df[12])
            self.field8.set(df[6])
            self.field9.set(df[7])
            self.field10.set(df[13])
        except:
            tk.messagebox.showerror("error","please enter valid ticket number")


    def close(self):
        self.clr()
        self.destroy()





class PassWindow(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)


        window_width = int((self.winfo_screenwidth() / 3))
        window_height = int((self.winfo_screenheight() / 8))

        xcord = (self.winfo_screenwidth()*2/3) // 2
        ycord = (self.winfo_screenheight()*7/8) // 2

        self.geometry(f"{window_width}x{window_height}+{int(xcord)}+{int(ycord)}")

        self.iconbitmap('myicon.ico')
        self.focus_set()
        self.title("Setting")

        frame2 = tk.Frame(self, bg='white')

        Label1_font = Font(family="Arquitecta", size=14)

        field_font = Font(family="Arquitecta", size=14)

        self.field1 = tk.StringVar()


        self.field_1_label = tk.Label(frame2, text='PASSWORD',fg="black",bg='white',font=Label1_font).grid(row=4,column=0, padx=6,pady=5)
        self.feild_1_value = tk.Entry(frame2,show="*",fg="black",bg='white',textvariable=self.field1, highlightthickness=2,highlightcolor='yellow',font=field_font,justify='center',exportselection=0)
        self.feild_1_value.bind("<Return>", lambda e: self.submit())
        self.feild_1_value.grid(row=4,column=1, padx=6,pady=5)

        frame2.pack(fill='both',expand=True)
        self.feild_1_value.focus_set()



    def submit(self):
        if (str(self.field1.get())=="ick4011" or str(self.field1.get())=="ICK4011"):
            self.clr()
            window = MultiTabWindow(self)
            window.grab_set()


        elif (str(self.field1.get())=="jaishreeram" or str(self.field1.get())=="JAISHREERAM"):
            data=db.Update_lic()
            tk.messagebox.showinfo("LICENCE",f"VALUE {data} SAVED... PLEASE RESTART SOFTWARE")
            self.close()

        elif (str(self.field1.get())=="settkt1" or str(self.field1.get())=="SETTKT1"):
            self.delall()
            self.close()


        else:
            self.field1.set("")


    def delall(self):
        try:
            if (len(self.field1.get())!=0):
                MsgBox = tk.messagebox.askquestion ('Are You Sure','Do you want to Delete all record?',icon = 'question')
                if MsgBox == 'yes':
                    rec=db.reset()
                    self.close()
                    MsgBox = tk.messagebox.showinfo("Done", str(rec)+" Records Deleted Successfully")
                else:
                    pass
            else:
                tk.messagebox.showerror("ERROR","RECORD CAN'T BE DELETED, TRY AGAIN")

        except:
            tk.messagebox.showerror("ERROR","RECORD CAN'T BE DELETED, TRY AGAIN")



    def close(self):
        self.clr()
        self.destroy()


    def clr(self):
        self.field1.set("")







if __name__ == "__main__":
    multiprocessing.freeze_support()
    login_window = LoginWindow()
    login_window.mainloop()










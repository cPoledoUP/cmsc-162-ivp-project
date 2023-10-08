#####################################################################
#   CMSC 162 - Introduction to Image and Video Processing Project   #
#####################################################################
#   Authors: Clent Japhet Poledo                                    #
#            Francis Albert Celeste                                 #
#####################################################################

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
from pcx_viewer import *
from matplotlib import pyplot as plt
import numpy as np
from tkinter import * 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import math

class App(tk.Tk):
    """
    Represents the app
    """
    
    def __init__(self, title, size, start_zoomed):

        # initialize
        super().__init__()
        self.title(title)
        self.geometry(size)
        if start_zoomed:
            self.state('zoomed')

        # add widgets
        self.menu_bar = Menubar(self)
        self.main = Main(self)
        # run the app
        self.mainloop()
        
    def menu_open(self):
        ftypes = [('pcx file', ['*.pcx']), ('image files', ['*.jpg', '*.png', '*.tiff', '*.ppm', '*.gif', '*.bmp'])]
        file = open(askopenfilename(parent=self, title='Select file', filetypes=ftypes))
        
        if file.name.endswith('.pcx'):
            self.pcx_image = PcxImage(file.name)
            self.image = PcxImage(file.name).get_image() # image data
            palette = PcxImage(file.name).get_image_palette(5)   # image color palette
            pcx_image = PcxImage(file.name) # to be used to retrieve metadata
            self.main.image_metadata.palette_frame.display_palette(palette)
            self.main.image_metadata.message.display_all(pcx_image)
            self.main.image_metadata.store_pcx_image(self.pcx_image)
            
        else:
            self.image = None
            image = Image.open(file.name)
            self.main.palette_frame.remove_palette()
            self.main.image_metadata.message.remove_display()
        
        self.main.image_frame.display_image(self.image)
        
        
    def menu_close(self):
        self.main.image_frame.remove_image()
        self.main.channel_frame.remove_image()
        self.main.image_metadata.palette_frame.remove_palette()
        self.main.image_metadata.message.remove_display()

class Menubar(tk.Menu):
    """
    Represents the top menu bar used in the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        parent['menu'] = self
        parent.option_add('*tearOff', False)

        # create the menu buttons
        filebutton = tk.Menu(self)
        filebutton.add_command(label="New", command=self.do_nothing)
        filebutton.add_command(label="Open", command=parent.menu_open)
        filebutton.add_command(label="Save", command=self.do_nothing)
        filebutton.add_command(label="Save as...", command=self.do_nothing)
        filebutton.add_command(label="Close", command=parent.menu_close)
        filebutton.add_separator()
        filebutton.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="File", menu=filebutton)

        editmenu = tk.Menu(self)
        editmenu.add_command(label="Undo", command=self.do_nothing)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.do_nothing)
        editmenu.add_command(label="Copy", command=self.do_nothing)
        editmenu.add_command(label="Paste", command=self.do_nothing)
        editmenu.add_command(label="Delete", command=self.do_nothing)
        editmenu.add_command(label="Select All", command=self.do_nothing)
        self.add_cascade(label="Edit", menu=editmenu)

        helpmenu = tk.Menu(self)
        helpmenu.add_command(label="Help Index", command=self.do_nothing)
        helpmenu.add_command(label="About...", command=self.do_nothing)
        self.add_cascade(label="Help", menu=helpmenu)
            
    def do_nothing(self):
        messagebox.showerror('Error!', 'This feature is not yet implemented!')

class Main(ttk.Frame):
    """
    Represents the main area of the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        # add widgets
        self.image_frame = ImageFrame(self)
        self.channel_frame = ChannelFrame(self)
        self.image_metadata = MetaDataFrame(self, tk.RIGHT)
        # self.grid(row=0,column=0,sticky="nwes")
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        self.pack(fill="both", expand=True)
        self.configure(relief=tk.SUNKEN)
        
class ImageFrame(tk.LabelFrame):
    """
    Contains the image display area of the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        self.pack(side = tk.LEFT, expand=True,padx=10, pady=10)
        self.label = tk.Label(self)
        self.label.pack()
        self.max_width = 500
        self.max_height = 240
        self.configure(relief="flat")

    def display_image(self, image):

        # resize image first to fit frame
        if float(image.size[0])/float(image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(image.size[0])
            hsize = int((float(image.size[1])*float(wpercent)))
            new_img = image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(image.size[1])
            wsize = int((float(image.size[0])*float(hpercent)))
            new_img = image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Original Image", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img

    def remove_image(self):
        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 30))
        self.label['image'] = None
        self.label.image = None
        
class ChannelFrame(tk.LabelFrame):
    """
    Contains the channel image display area of the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        
        self.pack(side = tk.LEFT, expand=True,padx=10, pady=10)
        self.label = tk.Label(self)
        self.label.pack()
        self.max_width = 500
        self.max_height = 240
        self.configure(relief="flat")

    def display_red_channel(self, image):

        # resize image first to fit frame
        if float(image.size[0])/float(image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(image.size[0])
            hsize = int((float(image.size[1])*float(wpercent)))
            new_img = image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(image.size[1])
            wsize = int((float(image.size[0])*float(hpercent)))
            new_img = image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Red Channel", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img
        
    def remove_image(self):
        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 30))
        self.label['image'] = None
        self.label.image = None


class PaletteFrame(tk.LabelFrame):
    """
    Contains the color palette used in the .pcx image
    """
    def __init__(self, parent):
        #initialize
        super().__init__(parent)
        self.pack(side = tk.BOTTOM, expand=True,padx=10, pady=10)
        self.label = tk.Label(self)
        self.label.pack()
        self.configure(relief="flat", bg='#808080')
        
    
    #displays the color palette of the image
    def display_palette(self, image):
        self.configure(labelanchor='n', text="COLOR PALETTE", font=('Helvetica Bold', 15))
        image = ImageTk.PhotoImage(image)
        self.label['image'] = image
        self.label.image = image

    def remove_palette(self):
        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 30))
        self.label['image'] = None
        self.label.image = None


class MetaDataFrame (tk.Frame):
    """
    Represents the Metadata frame
    """

    def __init__(self, parent, location):
        #initialize
        super().__init__(parent)
        self.image = PcxImage
        self.configure(bg='#808080', width=200, relief="flat")
        
        self.buttons_frame = Frame(self, highlightthickness=0)
        self.buttons_frame.pack(side = TOP, padx=20, pady=20)
        
        self.red_button = Button(self.buttons_frame, text='RED', state=DISABLED, command = lambda: parent.channel_frame.display_red_channel(self.image.show_color_channel_images('red')))
        self.red_button.pack(side=LEFT)
        
        self.green_button = Button(self.buttons_frame, text='GREEN', state=DISABLED)
        self.green_button.pack(side=LEFT)
        
        self.blue_button = Button(self.buttons_frame, text='BLUE', state=DISABLED)
        self.blue_button.pack(side=LEFT)
        
         # Create a frame for the message and pack it below the buttons
        self.message_frame = Frame(self, bd=0, highlightthickness=0)
        self.message_frame.pack(side=TOP, padx=20, pady=20)

        # Create the message widget
        self.message = MetaData(self.message_frame, red_button=self.red_button, blue_button=self.blue_button, green_button=self.green_button)
        
        # Create a frame for the palette_frame and pack it at the bottom
        self.palette_frame_frame = Frame(self, highlightthickness=0)
        self.palette_frame_frame.pack(side=TOP, padx=20, pady=20)

        # Create the palette_frame
        self.palette_frame = PaletteFrame(self.palette_frame_frame)

        self.pack(side=location, fill=tk.Y)
        
    def store_pcx_image(self, pcx_image):
        self.image = pcx_image
    
class MetaData (tk.Message):
    """
    the data retrieved from the Imported Image
    """ 

    def __init__(self, parent, red_button, green_button, blue_button):
        #initialize
        super().__init__(parent)
        self.red_button = red_button
        self.green_button = green_button
        self.blue_button = blue_button
        self.pack(side = tk.BOTTOM, expand=True,padx=10, pady=10)
        
        
    def display_all(self, image:PcxImage):
        header = "IMAGE METADATA:\n"
        all_data =  f"""
File Name: {image.location}
Manufacturer: {image.get_manufacturer()}
Version: {image.get_version()}
Encoding: {image.get_encoding()}
Bits per Pixel: {image.get_bits_per_pixel()}
Image Dimensions: {image.get_window()}
HDPI: {image.get_hdpi()}
VDPI: {image.get_vdpi()}
Number of Color Planes: {image.get_n_planes()}
Bytes per Line: {image.get_bytes_per_line()}
Palette Information: {image.get_palette_info()}
Horizontal Screen Size: {image.get_h_screen_size()}
Vertical Screen Size: {image.get_v_screen_size()}"""

        self.red_button.config(state=tk.NORMAL)
        self.green_button.config(state=tk.NORMAL)
        self.blue_button.config(state=tk.NORMAL)
        self.configure(bg='#808080', text= header + all_data, font=('Helvetica', 12))
        
    def remove_display(self):
        
        self.configure(bg='#808080', text="Open an Image", width=200, font=('Helvetica Bold', 30))
        self.red_button.config(state=tk.DISABLED)
        self.green_button.config(state=tk.DISABLED)
        self.blue_button.config(state=tk.DISABLED)

App("IVP App", "1280x720", True)
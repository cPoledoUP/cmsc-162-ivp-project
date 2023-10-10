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
# from tkinter import * 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import math

"""
Program module structure

.
└── App (Tk)
    ├── Menubar (Menu)
    └── Main (Frame)
        ├── ImageFrame (LabelFrame)
        ├── OutputFrame (LabelFrame)(previously ChannelFrame)
        └── MetadataFrame (Frame)
            ├── ToolBar (Frame)
            ├── Metadata (Message)
            └── PaletteFrame (LabelFrame)
"""

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
        # ftypes = [('pcx file', ['*.pcx']), ('image files', ['*.jpg', '*.png', '*.tiff', '*.ppm', '*.gif', '*.bmp'])]
        ftypes = [('pcx file', ['*.pcx'])]

        try:
            file = open(askopenfilename(parent=self, title='Select file', filetypes=ftypes))
            
            pcx_image = PcxImage(file.name) # to be used to retrieve metadata\
            if len(pcx_image.get_palette_data()) == 0:
                raise Exception("Unsupported pcx image: No palette at EOF")
        
            self.main.output_frame.remove_image()
            self.image = pcx_image.get_image() # image data
            palette = pcx_image.get_image_palette(5)   # image color palette
            self.main.image_metadata.palette_frame.display_palette(palette)
            self.main.image_metadata.message.display_all(pcx_image)
            self.main.image_metadata.tool_bar.enable_toolbar(pcx_image)
            self.main.image_frame.display_image(self.image)
            self.menu_bar.editmenu.entryconfig(7, command= lambda: self.main.output_frame.display_negative_image(pcx_image))
            file.close()
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror('Error', e)
        # else:
        #     self.image = Image(file.name)
        #     self.main.image_metadata.palette_frame.remove_palette()
        #     self.main.image_metadata.message.remove_display()
        
        
    def menu_close(self):
        self.main.image_frame.remove_image()
        self.main.output_frame.remove_image()
        self.main.image_metadata.palette_frame.remove_palette()
        self.main.image_metadata.message.remove_display()
        self.main.image_metadata.tool_bar.disable_toolbar()
        self.main.image_metadata.tool_bar.disable_slider()
        
class Menubar(tk.Menu):
    """
    Represents the top menu bar used in the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        self.parent = parent
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

        self.editmenu = tk.Menu(self)
        self.editmenu.add_command(label="Undo", command=self.do_nothing)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.do_nothing)
        self.editmenu.add_command(label="Copy", command=self.do_nothing)
        self.editmenu.add_command(label="Paste", command=self.do_nothing)
        self.editmenu.add_command(label="Delete", command=self.do_nothing)
        self.editmenu.add_command(label="Select All", command=self.do_nothing)
        self.editmenu.add_command(label="Negative", command=self.do_nothing)
        self.add_cascade(label="Edit", menu=self.editmenu)

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
        self.parent = parent
        # add widgets
        self.image_frame = ImageFrame(self)
        self.output_frame = OutputFrame(self)
        self.image_metadata = MetaDataFrame(self)
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
        self.parent = parent
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
        
class OutputFrame(tk.LabelFrame):
    """
    Contains the channel image display area of the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        self.parent = parent
        self.pack(side = tk.LEFT, expand=True,padx=10, pady=10)
        self.label = tk.Label(self)
        self.label.pack()
        self.canvas = None
        self.max_width = 500
        self.max_height = 240
        self.configure(relief="flat")

    def display_channel(self, pcx_image, color: str):
        image = pcx_image.show_color_channel_images(color)
        color_frequency = pcx_image.get_color_channels()[color]
        
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
        self.configure(labelanchor='n', text=f"{color.capitalize()} Channel", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img

        # remove existing histogram
        if self.canvas != None:
            self.canvas.get_tk_widget().pack_forget()
            
        # histogram for the color channel        
        fig, ax = plt.subplots(figsize = (5, 3))
        ax.hist(color_frequency, bins=256)

        self.canvas = FigureCanvasTkAgg(fig, 
                               master = self)
        self.canvas.get_tk_widget().pack(padx=20, pady=20)
        
    def display_negative_image(self, pcx_image):
        # remove existing image in frame first
        self.remove_image()
        
        negative_image = pcx_image.get_negative_image()
        
        # display the negative image 
        # resize image first to fit frame
        if float(negative_image.size[0])/float(negative_image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(negative_image.size[0])
            hsize = int((float(negative_image.size[1])*float(wpercent)))
            new_img = negative_image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(negative_image.size[1])
            wsize = int((float(negative_image.size[0])*float(hpercent)))
            new_img = negative_image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Negative Image", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img
        
    def display_grayscale_image (self, pcx_image):
        # remove existing image in frame first
        self.remove_image()    
        
        grey_image = pcx_image.get_grayscale_image('image')
        
        # display the negative image 
        # resize image first to fit frame
        if float(grey_image.size[0])/float(grey_image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(grey_image.size[0])
            hsize = int((float(grey_image.size[1])*float(wpercent)))
            new_img = grey_image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(grey_image.size[1])
            wsize = int((float(grey_image.size[0])*float(hpercent)))
            new_img = grey_image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Grayscale Image", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img
    
    def display_bnw_image(self, pcx_image, threshold):
        # remove existing image in frame first
        self.remove_image()    
        
        bnw_image = pcx_image.get_black_and_white_image(threshold)
        
        # display the black and white image 
        # resize image first to fit frame
        if float(bnw_image.size[0])/float(bnw_image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(bnw_image.size[0])
            hsize = int((float(bnw_image.size[1])*float(wpercent)))
            new_img = bnw_image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(bnw_image.size[1])
            wsize = int((float(bnw_image.size[0])*float(hpercent)))
            new_img = bnw_image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Black and White Image", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img
        
    def display_gamma_transformed_image(self, pcx_image, gamma):
        
        self.remove_image()    
        
        gamma_image = pcx_image.get_gamma_transformed_image(gamma)
        
        # display the gamma transformed image 
        # resize image first to fit frame
        if float(gamma_image.size[0])/float(gamma_image.size[1]) > self.max_width/self.max_height:
            wpercent = self.max_width/float(gamma_image.size[0])
            hsize = int((float(gamma_image.size[1])*float(wpercent)))
            new_img = gamma_image.resize((self.max_width, hsize))
        else:
            hpercent = self.max_height/float(gamma_image.size[1])
            wsize = int((float(gamma_image.size[0])*float(hpercent)))
            new_img = gamma_image.resize((wsize, self.max_height))

        # put image in the img_container
        self.configure(labelanchor='n', text="Gamma Transformed Image", font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img


    def remove_image(self):
        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 30))
        self.label['image'] = None
        self.label.image = None
        if self.canvas != None:
            self.canvas.get_tk_widget().pack_forget()

class MetaDataFrame (tk.Frame):
    """
    Represents the Metadata frame
    """

    def __init__(self, parent):
        #initialize
        super().__init__(parent, bg='#B0B0B0', width=250)
        self.parent = parent
        self.tool_bar = ToolBar(self)
        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill='x')
        
        
        # Create a frame for the message and pack it below the buttons
        # self.message_frame = tk.Frame(self, bd=0, highlightthickness=0)
        # self.message_frame.pack(side=tk.TOP, padx=20, pady=20)

        # Create the message widget
        self.message = MetaData(self)
        
        # Create a frame for the palette_frame and pack it at the bottom
        # self.palette_frame_frame = tk.Frame(self, highlightthickness=0)
        # self.palette_frame_frame.pack(side=tk.TOP, padx=20, pady=20)

        # Create the palette_frame
        self.palette_frame = PaletteFrame(self)

        self.pack(side=tk.RIGHT, fill=tk.Y)
        # self.pack_propagate(False) # disable resizing

class ToolBar(tk.Frame):
    """
    holds the buttons, sliders, and other input widgets
    """

    def __init__(self, parent):
        #initialize
        super().__init__(parent, highlightthickness=0)
        self.parent = parent

        self.pack(side = tk.TOP, padx=20, pady=20)

        # buttons
        self.red_button = tk.Button(self, text='RED',width=5, height= 1, fg='white', bg='red')
        self.red_button.grid(row=0, column=0, padx=2)
        
        self.green_button = tk.Button(self, text='GREEN',width=5, height= 1, fg='white', bg='green')
        self.green_button.grid(row=0, column=1, padx=2)
        
        self.blue_button = tk.Button(self, text='BLUE',width=5, height= 1, fg='white', bg='blue')
        self.blue_button.grid(row=0, column=2, padx=2)

        self.grey_scale_button = tk.Button(self, text='GREY',width=5, height= 1, fg='white', bg='gray')
        self.grey_scale_button.grid(row=1, column=0, padx=2, pady=(2,10))
        
        self.gamma_button = tk.Button(self, text='GAMM',width=5, height= 1, fg='black', bg='#d3d3d3')
        self.gamma_button.grid(row=1, column=1, padx=2, pady=(2,10))
        
        self.bw_button = tk.Button(self, text='B/W',width=5, height= 1, fg='black', bg='#d3d3d3')
        self.bw_button.grid(row=1, column=2, padx=2, pady=(2,10))
        
        self.bw_threshold_frame = tk.LabelFrame(self, text="B/W Threshold", bg='#fefefe', padx=20, pady=20)
        self.bw_threshold_frame.grid(row=2, columnspan=3)
        
        self.config(relief='flat', bg='#B0B0B0')
        
        """
        
        BLACK & WHITE SLIDER
        
        """
        
        self.current_value = tk.IntVar()
        
        #create slider
        self.bw_slider = ttk.Scale(
            self.bw_threshold_frame,
            from_= 0,
            to=255,
            orient='horizontal',
            command=self.slider_changed,
            variable= self.current_value
        )
        
        #set default to mid
        self.bw_slider.set(127)
        self.bw_slider.pack()
        
        #current value of the slider
        self.value = tk.Label(self.bw_threshold_frame, bg='#fefefe')
        self.value.pack(side="bottom")
        
        #current value LABEL of the slider
        self.value_label = tk.Label(self.bw_threshold_frame, text="Value:", padx=20, pady=5, bg='#fefefe')
        self.value_label.pack(side="bottom")
        
        #gamma input label
        self.gamma_input_label = tk.Label(self, text="Enter gamma: ", bg='#B0B0B0')
        self.gamma_input_label.grid(row=4, column=0, columnspan=2, pady=5, padx=0)
        
        #gamma input 
        self.gamma_threshold = tk.IntVar(None)
        self.gamma_input = tk.Entry(self, textvariable=self.gamma_threshold, width=7)
        self.gamma_input.grid(row=4, column=2, pady=5)
        
        # start disabled
        self.disable_toolbar()
        self.disable_slider()
        
    def get_scale_value(self):
        return '{: }'.format(self.current_value.get())
    
    def slider_changed(self, event):
        self.value.configure(text= self.get_scale_value())
        self.bw_button.invoke()
        
    def enable_slider(self):
        self.bw_slider['state'] = 'normal'

    def enable_toolbar(self, pcx_image):
        self.red_button.configure(command=lambda: [self.parent.parent.output_frame.display_channel(pcx_image, 'red'), self.disable_slider()], state=tk.NORMAL)
        self.green_button.configure(command=lambda: [self.parent.parent.output_frame.display_channel(pcx_image, 'green'), self.disable_slider()], state=tk.NORMAL)
        self.blue_button.configure(command=lambda: [self.parent.parent.output_frame.display_channel(pcx_image, 'blue'), self.disable_slider()], state=tk.NORMAL)
        self.grey_scale_button.configure(command=lambda: [self.parent.parent.output_frame.display_grayscale_image(pcx_image), self.disable_slider()], state=tk.NORMAL)
        self.gamma_button.configure(command= lambda: [self.check_entrybox(pcx_image),self.disable_slider()],state=tk.NORMAL)
        self.bw_button.configure(command=lambda: [self.parent.parent.output_frame.display_bnw_image(pcx_image, self.bw_slider.get()), self.enable_slider()] ,state=tk.NORMAL)
        self.gamma_input.configure(state=tk.NORMAL)
    
    def disable_slider(self):
        self.bw_slider['state'] = 'disabled'
    
    def disable_toolbar(self):
        self.red_button.config(state=tk.DISABLED)
        self.green_button.config(state=tk.DISABLED)
        self.blue_button.config(state=tk.DISABLED)
        self.grey_scale_button.config(state=tk.DISABLED)
        self.gamma_button.config(state=tk.DISABLED)
        self.bw_button.config(state=tk.DISABLED)
        self.gamma_input.delete(0, "end")
        self.gamma_input.config(state=tk.DISABLED)
        
    def check_entrybox(self, pcx_image):
        def isfloat(num):
            try:
                float(num)
                return True
            except ValueError:
                return False
            
        input = self.gamma_input.get().strip()
        if len(input) == 0:
            messagebox.showerror('Error!', 'Invalid gamma value. Please input positive float/integer values')  
        elif isfloat(input):
            if float(input) == 0:
                messagebox.showerror('Error!', 'Invalid gamma value. Please input positive float/integer values only')    
            elif input[0] == '-':
                messagebox.showerror('Error!', 'Please input positive float/integer values only')
            else:
                self.parent.parent.output_frame.display_gamma_transformed_image(pcx_image, float(input))
        else:
            messagebox.showerror('Error!', 'Invalid gamma value.')
            
            
class MetaData (tk.Message):
    """
    the data retrieved from the Imported Image
    """ 

    def __init__(self, parent):
        #initialize
        self.parent = parent
        super().__init__(parent)
        self.separator = ttk.Separator(parent, orient='horizontal')
        self.remove_display()
        
    def display_all(self, image:PcxImage):
        header = "IMAGE METADATA:\n"
        all_data = (
            f"File Name: {image.location}\n"
            f"Manufacturer: {image.get_manufacturer()}\n"
            f"Version: {image.get_version()}\n"
            f"Encoding: {image.get_encoding()}\n"
            f"Bits per Pixel: {image.get_bits_per_pixel()}\n"
            f"Image Dimensions: {image.get_window()}\n"
            f"HDPI: {image.get_hdpi()}\n"
            f"VDPI: {image.get_vdpi()}\n"
            f"Number of Color Planes: {image.get_n_planes()}\n"
            f"Bytes per Line: {image.get_bytes_per_line()}\n"
            f"Palette Information: {image.get_palette_info()}\n"
            f"Horizontal Screen Size: {image.get_h_screen_size()}\n"
            f"Vertical Screen Size: {image.get_v_screen_size()}"
        )
                    
        self.configure(bg='#B0B0B0', text= header + all_data, font=('Helvetica', 10), width=200)
        self.separator.pack(side= tk.BOTTOM, fill='x')
        self.pack(side = tk.BOTTOM, expand=True)
        
    def remove_display(self): 
        self.separator.pack_forget()
        self.pack_forget()

class PaletteFrame(tk.LabelFrame):
    """
    Contains the color palette used in the .pcx image
    """
    def __init__(self, parent):
        #initialize
        super().__init__(parent)
        self.parent = parent
        self.pack(side = tk.BOTTOM, expand=True,padx=10, pady=10)
        self.label = tk.Label(self)
        self.configure(relief="flat", bg='#B0B0B0')
        
    
    #displays the color palette of the image
    def display_palette(self, image):
        self.configure(labelanchor='n', text="COLOR PALETTE", font=('Helvetica Bold', 10))
        image = ImageTk.PhotoImage(image)
        self.label['image'] = image
        self.label.image = image
        self.label.pack()

    def remove_palette(self):
        self.label.pack_forget()
        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 10))
        self.label['image'] = None
        self.label.image = None

App("IVP App", "1280x720", True)
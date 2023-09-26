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
        
        ftypes = [('image files', ['*.pcx'])]
        file = open(askopenfilename(parent=self, title='Select file', filetypes=ftypes))
        pcxViewer = PcxImage(file.name)
        image = pcxViewer.get_image_palette()
        self.main.image_frame.display_image(image)
        
    # def menu_open(self):
    #     ftypes = [('image files', ['*.jpg', '*.png', '*.tiff', '*.ppm', '*.gif', '*.bmp'])]
    #     file = open(askopenfilename(parent=self, title='Select file', filetypes=ftypes))
    #     image = Image.open(file.name)
    #     self.main.image_frame.display_image(image)

    def menu_close(self):
        self.main.image_frame.remove_image()

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
        self.image_metadata = MetaDataFrame(self, tk.LEFT)
        self.image_frame = ImageFrame(self)
        self.image_metadata = MetaDataFrame(self, tk.RIGHT)
         
        # self.grid(row=0,column=0,sticky="nwes")
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        self.pack(fill="both", expand=True)
        self.configure(relief=tk.SUNKEN)
        
class ImageFrame(ttk.Label):
    """
    Contains the image display area of the app
    """

    def __init__(self, parent):

        # initialize
        super().__init__(parent)
        self.pack(side = tk.LEFT, expand=True,padx=10, pady=10)
        self.width = 960
        self.height = 720

    def display_image(self, image):

        # resize image first to fit frame
        if float(image.size[0])/float(image.size[1]) > self.width/self.height:
            wpercent = self.width/float(image.size[0])
            hsize = int((float(image.size[1])*float(wpercent)))
            new_img = image.resize((self.width, hsize))
        else:
            hpercent = self.height/float(image.size[1])
            wsize = int((float(image.size[0])*float(hpercent)))
            new_img = image.resize((wsize, self.height))

        # put image in the img_container
        new_img = ImageTk.PhotoImage(new_img)
        self['image'] = new_img
        self.image = new_img

    def remove_image(self):
        self['image'] = None
        self.image = None

class MetaDataFrame (tk.Frame):
    """
    Represents the Metadata frame
    """

    def __init__(self, parent, location):
        #initialize
        super().__init__(parent)
        self.message = MetaData(self)
        self.pack(side = location, fill=tk.Y)   
        self.configure(bg='blue', width=200, relief="raised")
        # self.label = ttk.Label(self)
        # self.label.pack(padx=20,pady=20)

class MetaData (tk.Message):
    """
    the data retrieved from the Imported Image
    """ 

    def __init__(self, parent):
        #initialize
        super().__init__(parent)
        self.configure(text="some data/ui elements go here", width=200, font=('Helvetica Bold', 30))
        self.pack(padx=10, pady=10, expand=True)

# matrix = [[(0, 0, 0) , (0, 0, 0) , (255, 0, 0) , (0, 0, 0) , (0, 0, 0) ], [(0, 0, 0) , (0, 0, 0) , (255, 0, 0) , (0, 0, 0) , (0, 0, 0) ]]

App("IVP App", "1280x720", True)
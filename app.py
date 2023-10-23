#####################################################################
#   CMSC 162 - Introduction to Image and Video Processing Project   #
#####################################################################
#   Authors: Clent Japhet Poledo                                    #
#            Francis Albert Celeste                                 #
#####################################################################

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter.filedialog import askopenfilename
from PIL import ImageTk
from pcx_viewer import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)

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
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        # add widgets
        self.menu_bar = Menubar(self)
        self.main = Main(self)

        # setup app
        self.setup_menu_buttons()
        self.bind_all('<KeyRelease>', self.on_key_release)

        # run the app
        self.mainloop()

        
    def menu_open(self):
        """
        Opens a pcx file
        """

        # ftypes = [('pcx file', ['*.pcx']), ('image files', ['*.jpg', '*.png', '*.tiff', '*.ppm', '*.gif', '*.bmp'])]
        ftypes = [('pcx file', ['*.pcx'])]

        try:
            file = open(askopenfilename(parent=self, title='Select file', filetypes=ftypes))

            pcx_image = PcxImage(file.name) # to be used to retrieve metadata
        
            self.main.output_frame.remove_image()
            self.image = pcx_image.get_image() # image data
            palette = pcx_image.get_image_palette(5)   # image color palette
            self.main.image_metadata.palette_frame.display_palette(palette)
            self.main.image_metadata.message.display_all(pcx_image)
            self.main.image_metadata.tool_bar.gamma_input.delete(0, "end")
            self.main.image_metadata.tool_bar.disable_slider()
            self.main.image_metadata.tool_bar.enable_toolbar(pcx_image)
            self.main.image_frame.display_image(self.image)
            file.close()
            self.menu_bar.entryconfig(2, state=tk.NORMAL)
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror('Error', e)
        # else:
        #     self.image = Image(file.name)
        #     self.main.image_metadata.palette_frame.remove_palette()
        #     self.main.image_metadata.message.remove_display()
        
        
    def menu_close(self):
        """
        Closes current image in app
        """
        self.menu_bar.entryconfig(2, state=tk.DISABLED)
        self.main.image_frame.remove_image()
        self.main.output_frame.remove_image()
        self.main.image_metadata.palette_frame.remove_palette()
        self.main.image_metadata.message.remove_display()
        self.main.image_metadata.tool_bar.disable_toolbar()
        self.main.image_metadata.tool_bar.disable_slider()
    
    def quit_app(self):
        """
        Exit the app
        """
        
        print("Exiting app...")
        self.quit()
        self.destroy()
        print("Exited successfully.")

    def setup_menu_buttons(self):
        """
        Make menu buttons functional
        """

        self.menu_bar.editmenu.entryconfig(0, command=self.main.image_metadata.tool_bar.red_button.invoke)
        self.menu_bar.editmenu.entryconfig(1, command=self.main.image_metadata.tool_bar.green_button.invoke)
        self.menu_bar.editmenu.entryconfig(2, command=self.main.image_metadata.tool_bar.blue_button.invoke)
        self.menu_bar.editmenu.entryconfig(4, command=self.main.image_metadata.tool_bar.grey_scale_button.invoke)
        self.menu_bar.editmenu.entryconfig(5, command=self.main.image_metadata.tool_bar.negative_button.invoke)
        self.menu_bar.editmenu.entryconfig(6, command=self.main.image_metadata.tool_bar.bw_button.invoke)
        self.menu_bar.editmenu.entryconfig(7, command=self.main.image_metadata.tool_bar.gamma_button.invoke)
        self.menu_bar.editmenu.entryconfig(9, command=self.main.image_metadata.tool_bar.averaging_filter_button.invoke)
        self.menu_bar.editmenu.entryconfig(10, command=self.main.image_metadata.tool_bar.median_filter_button.invoke)
        self.menu_bar.editmenu.entryconfig(11, command=self.main.image_metadata.tool_bar.highpass_filter_button.invoke)
        self.menu_bar.editmenu.entryconfig(12, command=self.main.image_metadata.tool_bar.unsharp_masking_button.invoke)
        self.menu_bar.editmenu.entryconfig(13, command=self.main.image_metadata.tool_bar.highboost_filter_button.invoke)
        self.menu_bar.editmenu.entryconfig(14, command=self.main.image_metadata.tool_bar.gradient_filter_button.invoke)
        self.menu_bar.editmenu.entryconfig(16, command=self.main.output_frame.show_histogram)
    
    def on_key_release(self, event):
        """
        Called on keyboard key release for keyboard shortcuts
        """
        
        if event.state == 4:  # keypress with Ctrl
            match event.keysym:
                case 'o' | 'O':
                    self.menu_bar.filebutton.invoke(0)  # open image
                case 'c'| 'C':
                    self.menu_bar.filebutton.invoke(1)  # close image
                case 'q'| 'Q':
                    self.menu_bar.filebutton.invoke(3)  # quit app
                case 'r' | 'R':
                    self.main.image_metadata.tool_bar.red_button.invoke()  # red button
                case 'g' | 'G':
                    self.main.image_metadata.tool_bar.green_button.invoke()  # green button
                case 'b' | 'B':
                    self.main.image_metadata.tool_bar.blue_button.invoke()  # blue button
                case '1':
                    self.main.image_metadata.tool_bar.averaging_filter_button.invoke()  # averaging filter button
                case '2':
                    self.main.image_metadata.tool_bar.median_filter_button.invoke() # median filter button
                case '3':
                    self.main.image_metadata.tool_bar.highpass_filter_button.invoke()   # highpass filter button
                case '4':
                    self.main.image_metadata.tool_bar.unsharp_masking_button.invoke()   # unsharp masking button
                case '5':
                    self.main.image_metadata.tool_bar.highboost_filter_button.invoke()  # highboost filter button
                case '6':
                    self.main.image_metadata.tool_bar.gradient_filter_button.invoke()   # gradient filter button
                case 'h' | 'H':
                    self.menu_bar.editmenu.invoke(16)
        else:
            match event.keysym:
                case 'F1':
                    self.main.image_metadata.tool_bar.grey_scale_button.invoke()    # grayscale button
                case 'F2':
                    self.main.image_metadata.tool_bar.negative_button.invoke()    # negative button
                case 'F3':
                    self.main.image_metadata.tool_bar.bw_button.invoke()    # black and white button
                case 'F4':
                    self.main.image_metadata.tool_bar.gamma_button.invoke()    # gamma button

        
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
        self.filebutton = tk.Menu(self)
        # filebutton.add_command(label="New", command=self.do_nothing)
        self.filebutton.add_command(label="Open (Ctrl+O)", command=parent.menu_open)
        # filebutton.add_command(label="Save", command=self.do_nothing)
        # filebutton.add_command(label="Save as...", command=self.do_nothing)
        self.filebutton.add_command(label="Close (Ctrl+C)", command=parent.menu_close)
        self.filebutton.add_separator()
        self.filebutton.add_command(label="Exit (Ctrl+Q)", command=parent.quit_app)
        self.add_cascade(label="File", menu=self.filebutton)

        self.editmenu = tk.Menu(self)
        # self.editmenu.add_command(label="Undo", command=self.do_nothing)
        # self.editmenu.add_separator()
        # self.editmenu.add_command(label="Cut", command=self.do_nothing)
        # self.editmenu.add_command(label="Copy", command=self.do_nothing)
        # self.editmenu.add_command(label="Paste", command=self.do_nothing)
        # self.editmenu.add_command(label="Delete", command=self.do_nothing)
        # self.editmenu.add_command(label="Select All", command=self.do_nothing)
        self.editmenu.add_command(label="Red Channel (Ctrl+R)", command=self.do_nothing)
        self.editmenu.add_command(label="Green Channel (Ctrl+G)", command=self.do_nothing)
        self.editmenu.add_command(label="Blue Channel (Ctrl+B)", command=self.do_nothing)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Grayscale (F1)", command=self.do_nothing)
        self.editmenu.add_command(label="Negative (F2)", command=self.do_nothing)
        self.editmenu.add_command(label="Black and White (F3)", command=self.do_nothing)
        self.editmenu.add_command(label="Gamma Transform (F4)", command=self.do_nothing)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Averaging Filter (Ctrl+1)", command=self.do_nothing)
        self.editmenu.add_command(label="Median Filter (Ctrl+2)", command=self.do_nothing)
        self.editmenu.add_command(label="Highpass Filtering (Ctrl+3)", command=self.do_nothing)
        self.editmenu.add_command(label="Unsharp Masking (Ctrl+4)", command=self.do_nothing)
        self.editmenu.add_command(label="Highboost Filtering (Ctrl+5)", command=self.do_nothing)
        self.editmenu.add_command(label="Gradient (Ctrl+6)", command=self.do_nothing)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Show Histogram (Ctrl+H)", command=self.do_nothing, state=tk.DISABLED)
        self.add_cascade(label="Edit", menu=self.editmenu, state=tk.DISABLED)

        # helpmenu = tk.Menu(self)
        # helpmenu.add_command(label="Help Index", command=self.do_nothing)
        self.add_command(label="About...", command=self.show_info)
        # self.add_cascade(label="Help", menu=helpmenu)
            
    def do_nothing(self):
        messagebox.showerror('Error!', 'This feature is not yet implemented!')
    
    def show_info(self):
        messagebox.showinfo("About", "Made for CMSC 162 Introduction to Image and Video Processing\n\nAuthors:\nClent Japhet Poledo\nFrancis Albert Celeste")

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
        self.pack(side = tk.LEFT, expand=False, padx=100, pady=10)
        self.label = tk.Label(self)
        self.label.pack()
        self.max_width = 500
        self.max_height = 240
        self.configure(relief="flat")

    def display_image(self, image):
        """
        Display the image in the frame
        """

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
        """
        Remove the image in the frame
        """

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
        self.hist_data = None
        self.canvas = None
        self.max_width = 500
        self.max_height = 240
        self.configure(relief="flat")

    def show_histogram(self):
        """
        Display the histogram of transformed image
        """

        # remove existing histogram
        if self.canvas != None:
            self.canvas.get_tk_widget().pack_forget()
            
        # histogram for the color channel        
        fig, ax = plt.subplots(figsize = (5, 3))
        ax.hist(self.hist_data, bins=256)

        self.canvas = FigureCanvasTkAgg(fig, 
                               master = self)
        self.canvas.get_tk_widget().pack(padx=20, pady=20)
        plt.close()
        
    def display_transformed_image(self, pcx_image: PcxImage, mode, *args):
        """
        Display the transformed image in the frame
        """

        # remove existing image in frame first
        self.remove_image()
        
        match mode:
            case 'RED':
                image = pcx_image.show_color_channel_images('red')
                label = 'Red Color Channel'
                self.hist_data = pcx_image.get_color_channels()['red']
            case 'GREEN':
                image = pcx_image.show_color_channel_images('green')
                label = 'Green Color Channel'
                self.hist_data = pcx_image.get_color_channels()['green']
            case 'BLUE':
                image = pcx_image.show_color_channel_images('blue')
                label = 'Blue Color Channel'
                self.hist_data = pcx_image.get_color_channels()['blue']
            case 'GREY':
                image = pcx_image.get_grayscale_image()
                label = 'Grayscale Image'
                self.hist_data = list(image.getdata())
            case 'NEG':
                image = pcx_image.get_negative_image()
                label = 'Negative Image'
                self.hist_data = list(image.getdata())
            case 'B/W':
                image = pcx_image.get_black_and_white_image(args[0])
                label = 'Black and White Image'
                self.hist_data = list(image.getdata())
            case 'GAMMA':
                image = pcx_image.get_gamma_transformed_image(args[0])
                label = 'Gamma Transformed Image'
                self.hist_data = list(image.getdata())
            case 'AVE':
                image = pcx_image.get_average_filtered_image(args[0])
                side_dimension = args[0] * 2 + 1
                label = f"Averaging Filter ({side_dimension}x{side_dimension})"
                self.hist_data = list(image.getdata())
            case 'MED':
                image = pcx_image.get_median_filtered_image(args[0])
                side_dimension = args[0] * 2 + 1
                label = f"Median Filter ({side_dimension}x{side_dimension})"
                self.hist_data = list(image.getdata())
            case 'HI':
                image = pcx_image.get_highpass_filtered_image(args[0])
                label = 'Highpass Filtering (Laplacian Operator)\n| 0  1  0 |\n| 1 -4  1 |\n| 0  1  0 |'
                self.hist_data = list(image.getdata())
            case 'UNSHARP':
                image = pcx_image.get_unsharp_masked_image()
                label = 'Unsharp Masking'
                self.hist_data = list(image.getdata())
            case 'HIBOOST':
                image = pcx_image.get_highboost_filtered_image(args[0])
                label = f"Highboost Filtering (A={args[0]})"
                self.hist_data = list(image.getdata())
            case 'EDGE':
                image = pcx_image.get_image_gradient()
                label = 'Gradient (Sobel Operator)'
                self.hist_data = list(image.getdata())
        
        # display the image 
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
        self.configure(labelanchor='n', text=label, font=('Helvetica Bold', 20))
        new_img = ImageTk.PhotoImage(new_img)
        self.label['image'] = new_img
        self.label.image = new_img

        self.parent.parent.menu_bar.editmenu.entryconfig(16, state=tk.NORMAL)

    def remove_image(self):
        """
        Remove the image in the frame
        """

        self.configure(labelanchor='n', text="", font=('Helvetica Bold', 30))
        self.label['image'] = None
        self.label.image = None
        self.hist_data = None
        if self.canvas != None:
            self.canvas.get_tk_widget().pack_forget()
        self.parent.parent.menu_bar.editmenu.entryconfig(16, state=tk.DISABLED)

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
        self.red_button = tk.Button(self, text='RED',width=7, height= 1, fg='white', bg='red')
        self.red_button.grid(row=0, column=0, padx=2)
        
        self.green_button = tk.Button(self, text='GREEN',width=7, height= 1, fg='white', bg='green')
        self.green_button.grid(row=0, column=1, padx=2)
        
        self.blue_button = tk.Button(self, text='BLUE',width=7, height= 1, fg='white', bg='blue')
        self.blue_button.grid(row=0, column=2, padx=2)

        self.grey_scale_button = tk.Button(self, text='GREY',width=7, height= 1, fg='white', bg='gray')
        self.grey_scale_button.grid(row=1, column=0, padx=2, pady=(2,10))
        
        self.negative_button = tk.Button(self, text='NEG',width=7, height= 1, fg='black', bg='#d3d3d3')
        self.negative_button.grid(row=1, column=1, padx=2, pady=(2,10))
        
        self.bw_button = tk.Button(self, text='B/W',width=7, height= 1, fg='black', bg='#d3d3d3')
        self.bw_button.grid(row=1, column=2, padx=2, pady=(2,10))
        
        self.bw_threshold_frame = tk.LabelFrame(self, text="B/W Threshold", bg='#fefefe', padx=20, pady=20)
        self.bw_threshold_frame.grid(row=2, columnspan=3)
        
        self.config(relief='flat', bg='#B0B0B0')
        
        """
        
        BLACK & WHITE SLIDER
        
        """
        
        #current value of the slider
        self.value = tk.Label(self.bw_threshold_frame, bg='#fefefe')
        self.value.pack(side="bottom")
        
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
        
        #current value LABEL of the slider
        self.value_label = tk.Label(self.bw_threshold_frame, text="Value:", padx=20, pady=5, bg='#fefefe')
        self.value_label.pack(side="bottom")
        
        #gamma input label
        self.gamma_input_label = tk.Label(self, text="Enter gamma: ", bg='#B0B0B0')
        self.gamma_input_label.grid(row=4, column=0, columnspan=2, pady=5, padx=0)
        
        #gamma input 
        # self.gamma_threshold = tk.StringVar()
        # self.gamma_threshold.set('1')
        self.gamma_input = tk.Entry(self, width=7)
        self.gamma_input.grid(row=4, column=2, pady=5)
        
        #create gamma button
        self.gamma_button = tk.Button(self, text='Gamma Transform', height= 1, fg='black', bg='#d3d3d3')
        self.gamma_button.grid(row=5, columnspan=3,  pady=(2,10))

        filter_button_label = tk.Label(self, text='Spatial Filtering', font=('Helvetica Bold', 10), bg='#b0b0b0', pady=5)
        filter_button_label.grid(row=6, column=0, columnspan=3)

        # filter buttons
        self.averaging_filter_button = tk.Button(self, text='AVE',width=7, height= 1)
        self.averaging_filter_button.grid(row=7, column=0, padx=2)
        self.median_filter_button = tk.Button(self, text='MED',width=7, height= 1)
        self.median_filter_button.grid(row=7, column=1, padx=2)
        self.highpass_filter_button = tk.Button(self, text='HI',width=7, height= 1)
        self.highpass_filter_button.grid(row=7, column=2, padx=2)
        self.unsharp_masking_button = tk.Button(self, text='UNSHARP',width=7, height= 1)
        self.unsharp_masking_button.grid(row=8, column=0, padx=2)
        self.highboost_filter_button = tk.Button(self, text='HIBOOST',width=7, height= 1)
        self.highboost_filter_button.grid(row=8, column=1, padx=2)
        self.gradient_filter_button = tk.Button(self, text='EDGE',width=7, height= 1)
        self.gradient_filter_button.grid(row=8, column=2, padx=2)
        
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
        self.red_button.configure(command=lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'RED'), self.disable_slider()], state=tk.NORMAL)
        self.green_button.configure(command=lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'GREEN'), self.disable_slider()], state=tk.NORMAL)
        self.blue_button.configure(command=lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'BLUE'), self.disable_slider()], state=tk.NORMAL)
        self.grey_scale_button.configure(command=lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'GREY'), self.disable_slider()], state=tk.NORMAL)
        self.negative_button.configure(command= lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'NEG'), self.disable_slider()], state=tk.NORMAL)
        self.gamma_button.configure(command= lambda: [self.check_entrybox(pcx_image),self.disable_slider()],state=tk.NORMAL)
        self.bw_button.configure(command=lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'B/W', self.bw_slider.get()), self.enable_slider()] ,state=tk.NORMAL)
        self.gamma_input.configure(state=tk.NORMAL)
        self.gamma_input.insert(0, '1')
        self.averaging_filter_button.configure(command= lambda: [self.show_ask_popup(pcx_image, 'AVE'), self.disable_slider()], state=tk.NORMAL)
        self.median_filter_button.configure(command= lambda: [self.show_ask_popup(pcx_image, 'MED'), self.disable_slider()], state=tk.NORMAL)
        self.highpass_filter_button.configure(command= lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'HI', 1), self.disable_slider()], state=tk.NORMAL)
        self.unsharp_masking_button.configure(command= lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'UNSHARP'), self.disable_slider()], state=tk.NORMAL)
        self.highboost_filter_button.configure(command= lambda: [self.show_ask_popup(pcx_image, 'HIBOOST'), self.disable_slider()], state=tk.NORMAL)
        self.gradient_filter_button.configure(command= lambda: [self.parent.parent.output_frame.display_transformed_image(pcx_image, 'EDGE'), self.disable_slider()], state=tk.NORMAL)

    def disable_slider(self):
        self.bw_slider['state'] = 'disabled'
    
    def disable_toolbar(self):
        self.red_button.config(state=tk.DISABLED)
        self.green_button.config(state=tk.DISABLED)
        self.blue_button.config(state=tk.DISABLED)
        self.grey_scale_button.config(state=tk.DISABLED)
        self.negative_button.config(state=tk.DISABLED)
        self.bw_button.config(state=tk.DISABLED)
        self.gamma_button.config(state=tk.DISABLED)
        self.gamma_input.delete(0, "end")
        self.gamma_input.config(state=tk.DISABLED)
        self.averaging_filter_button.config(state=tk.DISABLED)
        self.median_filter_button.config(state=tk.DISABLED)
        self.highpass_filter_button.config(state=tk.DISABLED)
        self.unsharp_masking_button.config(state=tk.DISABLED)
        self.highboost_filter_button.config(state=tk.DISABLED)
        self.gradient_filter_button.config(state=tk.DISABLED)
        
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
                self.parent.parent.output_frame.display_transformed_image(pcx_image, 'GAMMA', float(input))
        else:
            messagebox.showerror('Error!', 'Invalid gamma value.')
    
    def show_ask_popup(self, pcx_image, mode):
        match mode:
            case 'AVE':
                input_val = simpledialog.askinteger('Averaging Filter', 'Enter side radius of desired mask (e.g., 1 for 3x3, 2 for 5x5)', initialvalue=1, minvalue=1, maxvalue=5)
                if input_val != None:
                    self.parent.parent.output_frame.display_transformed_image(pcx_image, 'AVE', input_val)
            case 'MED':
                input_val = simpledialog.askinteger('Median Filter', 'Enter side radius of desired mask (e.g., 1 for 3x3, 2 for 5x5)', initialvalue=1, minvalue=1, maxvalue=5)
                if input_val != None:
                    self.parent.parent.output_frame.display_transformed_image(pcx_image, 'MED', input_val)
            case 'HIBOOST':
                input_val = simpledialog.askinteger('Highboost Filter', 'Enter side radius of desired "A" value', initialvalue=2, minvalue=1)
                if input_val != None:
                    self.parent.parent.output_frame.display_transformed_image(pcx_image, 'HIBOOST', input_val)
            
            
class MetaData (tk.Text):
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
        scroll = ttk.Scrollbar(self.parent, command=self.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        header = "IMAGE METADATA:\n\n"
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
        self.insert('1.0', header + all_data)
        self.configure(bg='#B0B0B0', font=('Helvetica', 10), padx=10, pady=10, width=25, relief='flat', state='disabled', yscrollcommand=scroll.set)
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
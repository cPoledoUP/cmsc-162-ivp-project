import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text="widget info"):
        self.waittime = 500  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx()
        y += self.widget.winfo_rooty() - 15
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength,
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class ToolTipButton(ttk.Button):
    def __init__(self, parent, image, tooltip, text=None):
        if text:
            ttk.Style().configure("TButton", foreground="white", font="None 10 bold")
            super().__init__(
                parent,
                image=image,
                text=text,
                compound="center",
                width=1,
            )
        else:
            super().__init__(parent, image=image, compound="center", width=1)
        CreateToolTip(self, text=tooltip)


class ImageFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, relief="solid")
        self.image = None
        self.image_label = ttk.Label(self)
        self.image_label.pack(expand=True)

    def display_image(self, image: Image):
        # resize image first to fit frame
        max_width = self.winfo_width() - 10
        max_height = self.winfo_height() - 10
        width, height = image.size

        if width / height > max_width / max_height:
            wpercent = max_width / width
            hsize = int(height * wpercent)
            new_img = image.resize((max_width, hsize))
        else:
            hpercent = max_height / height
            wsize = int(width * hpercent)
            new_img = image.resize((wsize, max_height))

        self.image = ImageTk.PhotoImage(new_img)
        self.image_label.configure(image=self.image)

    def remove_image(self):
        self.image = None
        self.image_label.configure(image=None)

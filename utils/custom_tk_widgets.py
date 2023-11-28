import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt


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
    def __init__(self, parent, image, tooltip, text=None, command=None):
        if text:
            ttk.Style().configure(
                "Tooltip.TButton", foreground="white", font="None 10 bold"
            )
            super().__init__(
                parent,
                image=image,
                text=text,
                compound="center",
                width=1,
                style="Tooltip.TButton",
                command=command,
            )
        else:
            super().__init__(
                parent, image=image, compound="center", width=1, command=command
            )
        CreateToolTip(self, text=tooltip)


class ImageFrame(ttk.Frame):
    def __init__(self, parent, closable=True, title=None, info=None):
        super().__init__(parent, relief="solid")
        self.parent = parent
        self.image = None
        self.image_data = None
        self.title = title
        self.image_label = ttk.Label(self, anchor="center")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        self.histogram_button = ttk.Button(
            self.image_label, text="Histogram", command=self.show_hist
        )
        self.progress_bar = ttk.Progressbar(
            self.image_label, orient="horizontal", mode="indeterminate", length=280
        )
        if closable:
            close_button = ttk.Button(
                self.image_label, text="X", width=3, command=self.close_tab
            )
            close_button.pack(anchor="ne")
        if info:
            info_button = ttk.Button(
                self.image_label, text="?", width=3, command=self.open_info
            )
            info_button.pack(anchor="ne")
            self.info = info

    def display_image(self, image: Image, resize=True, show_histogram=True):
        if show_histogram:
            self.image_data = list(image.getdata())
            self.histogram_button.pack(anchor="ne")
        if resize:
            # resize image first to fit frame
            max_width = self.winfo_width() - 10
            max_height = self.winfo_height() - 10

            width, height = image.size
            if width / height > max_width / max_height:
                wpercent = max_width / width
                hsize = int(height * wpercent)
                image = image.resize((max_width, hsize))
            else:
                hpercent = max_height / height
                wsize = int(width * hpercent)
                image = image.resize((wsize, max_height))

        self.image = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.image)

    def remove_image(self):
        self.image_data = None
        self.image = None
        self.image_label.configure(image=None)
        self.histogram_button.pack_forget()

    def close_tab(self):
        self.parent.forget(self.parent.select())

    def open_info(self):
        messagebox.showinfo("Image information", message=self.info)

    def show_hist(self):
        self.start_loading()
        fig = plt.figure()
        ax = fig.add_subplot()

        if type(self.image_data[0]) is int:
            ax.hist(self.image_data, 256, (0, 255))
        else:
            r, g, b = zip(*self.image_data)
            if self.title == "Red Channel":
                ax.hist(r, 256, (0, 255))
            elif self.title == "Green Channel":
                ax.hist(g, 256, (0, 255))
            elif self.title == "Blue Channel":
                ax.hist(b, 256, (0, 255))
            else:
                ax.hist(r, 256, (0, 255), label="Red Channel")
                ax.hist(g, 256, (0, 255), label="Green Channel")
                ax.hist(b, 256, (0, 255), label="Blue Channel")
        self.stop_loading()

        if self.title:
            plt.title(self.title)
        else:
            plt.title("Image Histogram")
            plt.legend(loc="upper right")
        plt.xlabel("Color Value")
        plt.ylabel("Frequency")
        plt.show()

    def start_loading(self):
        self.progress_bar.pack(expand=True)
        self.progress_bar.start(10)
        self.image_label.update()

    def stop_loading(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()


class ChoiceDialog(tk.Toplevel):
    def __init__(self, root, title, prompt, choices, map_val=None):
        super().__init__(root)

        self.map_val = map_val
        self.choices = choices

        self.title = title
        ttk.Label(self, text=prompt).pack(expand=True, pady=5, padx=5)
        self.combobox = ttk.Combobox(self, values=choices)
        self.combobox.pack(pady=5, padx=5)
        self.combobox.current(0)
        ttk.Button(self, text="Submit", command=self.buttonfn).pack(pady=5, padx=5)

        self.result = None

    def buttonfn(self):
        if self.map_val:
            self.result = self.map_val[self.choices.index(self.combobox.get())]
        self.result = self.combobox.get()
        self.destroy()


def ask_choice(root, title, prompt, choices, map_val=None):
    global result
    result = None

    def button():
        global result
        result = combobox.get()
        if map_val:
            result = map_val[choices.index(result)]
        top.destroy()

    top = tk.Toplevel(root)
    top.title = title

    ttk.Label(top, text=prompt).pack(expand=True, pady=5, padx=5)
    combobox = ttk.Combobox(top, values=choices, width=30, state="readonly")
    combobox.pack(pady=5, padx=5)
    combobox.current(0)
    ttk.Button(top, text="Submit", command=button).pack(pady=5, padx=5)

    top.update_idletasks()
    top.geometry(
        f"+{int(root.winfo_width() / 2 - top.winfo_width() / 2)}+{int(root.winfo_height() / 2 - top.winfo_height() / 2)}"
    )
    top.grab_set()
    root.wait_window(top)

    return result

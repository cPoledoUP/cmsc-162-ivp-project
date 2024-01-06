#####################################################################
#   CMSC 162 - Introduction to Image and Video Processing Project   #
#####################################################################
#   Authors: Clent Japhet Poledo                                    #
#            Francis Albert Celeste                                 #
#####################################################################

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from utils.custom_tk_widgets import ToolTipButton, ImageFrame, ask_choice
from utils.button_icon_gen import IvpBtnIcon
from utils.image_parser import ImageParser
from utils.image_processor import ImageProcessor
import zipfile

# App globals
CURRENT_IMAGE = None
GRAYSCALE_DATA = None
LAST_NOISED_DATA = None

########## FUNCTIONS ##########


def show_about():
    messagebox.showinfo(
        "About",
        "Made for CMSC 162 Introduction to Image and Video Processing\n\nAuthors:\nClent Japhet Poledo\nFrancis Albert Celeste",
    )


def open_file():
    global CURRENT_IMAGE
    global GRAYSCALE_DATA

    file_types = [("Image Files", ["*.pcx", "*.jpg", "*.jpeg", "*.png", "*.bmp"]), ("Compressed Image", ["*.zip"])]
    filename = filedialog.askopenfilename(
        title="Open an image file", filetypes=file_types
    )
    if filename:
        # extract all images if compressed
        if filename.endswith("zip"):
            with zipfile.ZipFile(filename, "r") as archive:
                namelist = archive.namelist()
                archive.extractall(filename[:-4])
                # remove the empty .zip file in the output folder
                filename = ["/".join([filename[:-4], name]) for name in namelist]

        # load single image
        else:
            filename = [filename]
        
        for i in range(len(filename)):
            main_notebook.select(0)
            current_frame = None
            try:
                # for the first image, put it in the main frame
                if i == 0:
                    current_frame = main_frame
                    current_frame.start_loading()
                    CURRENT_IMAGE = ImageParser.parse_image(filename[i])
                    main_frame.display_image(
                        ImageProcessor.get_displayable_image(
                            CURRENT_IMAGE["pixel_data"],
                            CURRENT_IMAGE["width"],
                            CURRENT_IMAGE["height"],
                        )
                    )
                    metadata_title.configure(text="Image Metadata")
                    metadata_label.configure(text=CURRENT_IMAGE["metadata"])
                    if CURRENT_IMAGE["palette_data"]:
                        palette_title.configure(text="Color Palette")
                        palette_image.display_image(
                            ImageProcessor.get_displayable_palette(
                                CURRENT_IMAGE["palette_data"], 10
                            ),
                            False,
                            False,
                        )
                        palette_image.pack(pady=10)
                    else:
                        palette_title.configure(text="")
                        palette_image.remove_image()
                        palette_image.pack_forget()

                    GRAYSCALE_DATA = list(
                        ImageProcessor.get_grayscale_image(
                            CURRENT_IMAGE["pixel_data"],
                            CURRENT_IMAGE["width"],
                            CURRENT_IMAGE["height"],
                        ).getdata()
                    )

                # for the rest, in a new tab
                else:
                    new_frame = ImageFrame(main_notebook, title=f"img{i}")
                    new_frame.pack(fill="both", expand=True)
                    main_notebook.add(new_frame, text=f"img{i}")
                    main_notebook.select(new_frame)
                    current_frame = new_frame
                    current_frame.start_loading()
                    img_to_disp = ImageParser.parse_image(filename[i])
                    new_frame.display_image(
                        ImageProcessor.get_displayable_image(
                            img_to_disp["pixel_data"],
                            img_to_disp["width"],
                            img_to_disp["height"],
                        )
                    )
                current_frame.stop_loading()

            except Exception as e:
                current_frame.stop_loading()
                messagebox.showerror("Error opening file", str(e))


def process_image(mode):
    current_frame = main_notebook.nametowidget(main_notebook.select())
    try:
        if not CURRENT_IMAGE:
            raise Exception("Load an image first")

        image_data = CURRENT_IMAGE["pixel_data"]
        grayscale_data = GRAYSCALE_DATA
        width = CURRENT_IMAGE["width"]
        height = CURRENT_IMAGE["height"]
        global LAST_NOISED_DATA
        info = None
        current_frame.start_loading()

        match mode:
            case "Red Channel":
                image = ImageProcessor.show_color_channel_images(
                    image_data, width, height, "red"
                )
            case "Green Channel":
                image = ImageProcessor.show_color_channel_images(
                    image_data, width, height, "green"
                )
            case "Blue Channel":
                image = ImageProcessor.show_color_channel_images(
                    image_data, width, height, "blue"
                )
            case "Grayscale Transform":
                image = ImageProcessor.get_grayscale_image(image_data, width, height)
                info = "Transformation function: (r + g + b) / 3"
            case "Negative Transform":
                image = ImageProcessor.get_negative_image(grayscale_data, width, height)
            case "Black and White Transform":
                threshold = simpledialog.askinteger(
                    mode,
                    "Enter threshold value",
                    initialvalue=0,
                    minvalue=0,
                    maxvalue=255,
                )
                if threshold == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor.get_black_and_white_image(
                    grayscale_data, width, height, threshold
                )
                info = f"Threshold Value: {threshold}"
            case "Gamma Transform":
                gamma = simpledialog.askfloat(
                    mode, "Enter gamma", initialvalue=1, minvalue=0
                )
                if gamma == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor.get_gamma_transformed_image(
                    grayscale_data, width, height, gamma
                )
                info = f"Gamma: {gamma}"
            case "Averaging Filter":
                choices = ["3x3", "5x5", "7x7", "9x9"]
                choices_map = [1, 2, 3, 4]
                radius = ask_choice(
                    root, mode, "Choose mask size", choices, choices_map
                )
                if radius == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().get_average_filtered_image(
                    grayscale_data, width, height, radius
                )
                info = f"Mask: {2*radius+1}x{2*radius+1}"
            case "Median Filter":
                choices = ["3x3", "5x5", "7x7", "9x9"]
                choices_map = [1, 2, 3, 4]
                radius = ask_choice(
                    root, mode, "Choose mask size", choices, choices_map
                )
                if radius == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().get_median_filtered_image(
                    grayscale_data, width, height, radius
                )
                info = f"Mask: {2*radius+1}x{2*radius+1}"
            case "Highpass Filter":
                choices = [
                    "[0, 1, 0, 1, -4, 1, 0, 1, 0]",
                    "[0, -1, 0, -1, 4, -1, 0, -1, 0]",
                    "[1, 1, 1, 1, -8, 1, 1, 1, 1]",
                    "[-1, -1, -1, -1, 8, -1, -1, -1, -1]",
                ]
                choices_map = [1, 2, 3, 4]
                filter = ask_choice(
                    root, mode, "Choose laplacian filter", choices, choices_map
                )
                if filter == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().get_highpass_filtered_image(
                    grayscale_data, width, height, filter
                )
                info = f"Filter used: {choices[choices_map.index(filter)]}"
            case "Unsharp Masking":
                image = ImageProcessor().get_unsharp_masked_image(
                    grayscale_data, width, height
                )
            case "Highboost Filter":
                a = simpledialog.askfloat(
                    mode, "Enter A value", initialvalue=2, minvalue=1
                )
                if a == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().get_highboost_filtered_image(
                    grayscale_data, width, height, a
                )
                info = f"A: {a}"
            case "Image Gradient":
                choices = ["both", "x", "y"]
                choices_map = [1, 2, 3]
                direction = ask_choice(
                    root, mode, "Choose gradient direction", choices, choices_map
                )
                if direction == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().get_image_gradient(
                    grayscale_data, width, height, direction
                )
                info = f"Gradient direction: {choices[choices_map.index(direction)]}"
            case "Salt and Pepper Noise":
                probability = simpledialog.askfloat(
                    mode,
                    "Enter salt and pepper probability",
                    initialvalue=0,
                    minvalue=0,
                    maxvalue=0.5,
                )
                if probability == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor.apply_salt_pepper(
                    grayscale_data, width, height, probability
                )
                info = f"Salt and pepper probability: {probability}"
                LAST_NOISED_DATA = list(image.getdata())
            case "Gaussian Noise":
                image = ImageProcessor.apply_gaussian(grayscale_data, width, height)
                LAST_NOISED_DATA = list(image.getdata())
            case "Erlang Noise":
                image = ImageProcessor.apply_erlang(grayscale_data, width, height)
                LAST_NOISED_DATA = list(image.getdata())
            case "Geometric Mean Filter":
                if not LAST_NOISED_DATA:
                    raise Exception("Perform an image degradation operation first.")
                image = ImageProcessor().add_geometric_filter(
                    width, height, LAST_NOISED_DATA
                )
            case "Contraharmonic Mean Filter":
                if not LAST_NOISED_DATA:
                    raise Exception("Perform an image degradation operation first.")
                q = simpledialog.askfloat(mode, "Enter q value", initialvalue=0)
                if q == None:
                    raise Exception("Cancelled operation")
                image = ImageProcessor().add_contraharmonic(
                    width, height, LAST_NOISED_DATA, q
                )
                info = f"q value: {q}"
            case "Order-Statistics Filter":
                if not LAST_NOISED_DATA:
                    raise Exception("Perform an image degradation operation first.")
                image = ImageProcessor().get_median_filtered_image(
                    LAST_NOISED_DATA, width, height
                )
                info = "Filter used: 3x3 median filter"
            case "Run-length Encoding":
                rle_data, palette, size_info = ImageProcessor.run_length_encoding(
                    image_data
                )
                image = ImageProcessor.run_length_decode(
                    rle_data, palette, width, height
                )
                orig_info = ImageProcessor.get_uncompressed_image_size(image_data)
                info = "Uncompressed Image Information\n"
                info += f"Image size: {orig_info["image size"]} bytes\n"
                info += f"Palette size: {orig_info["palette size"]} bytes\n"
                info += "\nRun-length Encoded Image Information\n"
                info += f"Image size: {size_info["image size"]} bytes\n"
                info += f"Palette size: {size_info["palette size"]} bytes\n"
                info += "\nCompression Ratio\n"
                info += f"Image data only: {orig_info["image size"] / size_info["image size"]}"
                info += f"\nImage data and palette info: {(orig_info["image size"] + orig_info["palette size"]) / (size_info["image size"] + size_info["palette size"])}"
            case "Huffman Coding":
                huffman_data, huffman_codes, size_info = ImageProcessor.huffman_coding(
                    image_data
                )
                image = ImageProcessor.huffman_decode(
                    huffman_data, huffman_codes, width, height
                )
                orig_info = ImageProcessor.get_uncompressed_image_size(image_data)
                info = "Uncompressed Image Information\n"
                info += f"Image size: {orig_info["image size"]} bytes\n"
                info += f"Palette size: {orig_info["palette size"]} bytes\n"
                info += "\nHuffman Coded Image Information\n"
                info += f"Image size: {size_info["image size"]} bytes\n"
                info += f"Huffman codes size: {size_info["huffman codes size"]} bytes\n"
                info += "\nCompression Ratio\n"
                info += f"Image data only: {orig_info["image size"] / size_info["image size"]}"
                info += f"\nImage data and huffman codes: {(orig_info["image size"] + orig_info["palette size"]) / (size_info["image size"] + size_info["huffman codes size"])}"

            case _:
                current_frame.stop_loading()
                return

        current_frame.stop_loading()
        new_frame = ImageFrame(main_notebook, title=mode, info=info)
        new_frame.pack(fill="both", expand=True)
        if len(main_notebook.tabs()) >= 5:
            main_notebook.forget(1)
        main_notebook.add(new_frame, text=mode)
        main_notebook.select(new_frame)
        new_frame.display_image(image)
    except Exception as e:
        current_frame.stop_loading()
        if str(e) != "Cancelled operation":
            messagebox.showerror("Error", str(e))


########## PLACEMENT OF UI ELEMENTS ##########

# setup the root of the app
root = tk.Tk()
root.title("Image Processing App")
root.geometry("1280x720")
root.state("zoomed")

# configure styling
# ttk.Style().configure("TFrame", background="#121212")

##### setup menu buttons
menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(label="Open image", command=open_file, accelerator="Ctrl+O")
menubar.add_cascade(label="File", menu=file_menu)
menubar.add_command(label="About...", command=show_about)

##### setup main frame
main_notebook = ttk.Notebook(root)
main_notebook.pack(side="left", fill="both", expand=True)

main_frame = ImageFrame(main_notebook, closable=False)
main_frame.pack(fill="both", expand=True)

main_notebook.add(main_frame, text="Original")

##### setup sidebar frame
sidebar = ttk.Notebook(root, width=200)
sidebar.pack(side="right", fill="y")

buttons_frame = ttk.Frame(sidebar, relief="solid", padding=10)
buttons_frame.pack(fill="both", expand=True)
metadata_frame = ttk.Frame(sidebar, relief="solid", padding=10)
metadata_frame.pack(fill="both", expand=True)

sidebar.add(buttons_frame, text="Edit")
sidebar.add(metadata_frame, text="Metadata")

# setup sidebar buttons
# color buttons
dark_btn_icon = IvpBtnIcon.black()
color_btn_label = ttk.Label(buttons_frame, text="Color Channels")
red_btn_icon = IvpBtnIcon.red()
red_btn = ToolTipButton(
    buttons_frame,
    image=red_btn_icon,
    tooltip="Red Channel",
    command=lambda: process_image("Red Channel"),
)
green_btn_icon = IvpBtnIcon.green()
green_btn = ToolTipButton(
    buttons_frame,
    image=green_btn_icon,
    tooltip="Green Channel",
    command=lambda: process_image("Green Channel"),
)
blue_btn_icon = IvpBtnIcon.blue()
blue_btn = ToolTipButton(
    buttons_frame,
    image=blue_btn_icon,
    tooltip="Blue Channel",
    command=lambda: process_image("Blue Channel"),
)
# image transform buttons
img_trans_label = ttk.Label(buttons_frame, text="Image Transformation")
gray_btn_icon = IvpBtnIcon.grayscale()
gray_btn = ToolTipButton(
    buttons_frame,
    image=gray_btn_icon,
    tooltip="Grayscale Transform",
    command=lambda: process_image("Grayscale Transform"),
)
neg_btn_icon = IvpBtnIcon.black()
neg_btn = ToolTipButton(
    buttons_frame,
    image=neg_btn_icon,
    tooltip="Negative Transform",
    text="+/-",
    command=lambda: process_image("Negative Transform"),
)
bnw_btn_icon = IvpBtnIcon.black_and_white()
bnw_btn = ToolTipButton(
    buttons_frame,
    image=bnw_btn_icon,
    tooltip="Black and White Transform",
    command=lambda: process_image("Black and White Transform"),
)
gamma_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Gamma Transform",
    text="γ",
    command=lambda: process_image("Gamma Transform"),
)
# spatial filter buttons
filter_label = ttk.Label(buttons_frame, text="Spatial Filtering")
ave_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Averaging Filter",
    text="x̄",
    command=lambda: process_image("Averaging Filter"),
)
med_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Median Filter",
    text="x͂",
    command=lambda: process_image("Median Filter"),
)
hipass_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Highpass Filter",
    text="HI",
    command=lambda: process_image("Highpass Filter"),
)
unsharp_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Unsharp Masking",
    text="U",
    command=lambda: process_image("Unsharp Masking"),
)
hiboost_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Highboost Filter",
    text="HB",
    command=lambda: process_image("Highboost Filter"),
)
gradient_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Image Gradient",
    text="G",
    command=lambda: process_image("Image Gradient"),
)
# image degradation buttons
img_deg_label = ttk.Label(buttons_frame, text="Image Degradation")
salt_pepper_btn_icon = IvpBtnIcon.salt_and_pepper()
salt_pepper_btn = ToolTipButton(
    buttons_frame,
    image=salt_pepper_btn_icon,
    tooltip="Salt and Pepper Noise",
    command=lambda: process_image("Salt and Pepper Noise"),
)
gauss_btn_icon = IvpBtnIcon.gauss()
gauss_btn = ToolTipButton(
    buttons_frame,
    image=gauss_btn_icon,
    tooltip="Gaussian Noise",
    command=lambda: process_image("Gaussian Noise"),
)
erlang_btn_icon = IvpBtnIcon.erlang()
erlang_btn = ToolTipButton(
    buttons_frame,
    image=erlang_btn_icon,
    tooltip="Erlang Noise",
    command=lambda: process_image("Erlang Noise"),
)
# image restoration buttons
img_res_label = ttk.Label(buttons_frame, text="Image Restoration")
geometric_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Geometric Mean Filter",
    text="Π",
    command=lambda: process_image("Geometric Mean Filter"),
)
contraharm_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Contraharmonic Mean Filter",
    text="Σ/Σ",
    command=lambda: process_image("Contraharmonic Mean Filter"),
)
ordstat_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Order-Statistics Filter",
    text="x͂",
    command=lambda: process_image("Order-Statistics Filter"),
)
# image compression buttons
img_comp_label = ttk.Label(buttons_frame, text="Image Compression")
rle_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Run-length Encoding",
    text="RLE",
    command=lambda: process_image("Run-length Encoding"),
)
huffman_btn = ToolTipButton(
    buttons_frame,
    image=dark_btn_icon,
    tooltip="Huffman Coding",
    text="HC",
    command=lambda: process_image("Huffman Coding"),
)

# display the sidebar elements
pady = 2
color_btn_label.grid(column=0, row=0, columnspan=3, pady=5, sticky="w")
red_btn.grid(column=0, row=1, padx=5, pady=pady)
green_btn.grid(column=1, row=1, padx=5, pady=pady)
blue_btn.grid(column=2, row=1, padx=5, pady=pady)
img_trans_label.grid(column=0, row=2, columnspan=3, pady=5, sticky="w")
gray_btn.grid(column=0, row=3, padx=5, pady=pady)
neg_btn.grid(column=1, row=3, padx=5, pady=pady)
bnw_btn.grid(column=2, row=3, padx=5, pady=pady)
gamma_btn.grid(column=0, row=4, padx=5, pady=pady)
filter_label.grid(column=0, row=5, columnspan=3, pady=5, sticky="w")
ave_btn.grid(column=0, row=6, padx=5, pady=pady)
med_btn.grid(column=1, row=6, padx=5, pady=pady)
hipass_btn.grid(column=2, row=6, padx=5, pady=pady)
unsharp_btn.grid(column=0, row=7, padx=5, pady=pady)
hiboost_btn.grid(column=1, row=7, padx=5, pady=pady)
gradient_btn.grid(column=2, row=7, padx=5, pady=pady)
img_deg_label.grid(column=0, row=8, columnspan=3, pady=5, sticky="w")
salt_pepper_btn.grid(column=0, row=9, padx=5, pady=pady)
gauss_btn.grid(column=1, row=9, padx=5, pady=pady)
erlang_btn.grid(column=2, row=9, padx=5, pady=pady)
img_res_label.grid(column=0, row=10, columnspan=3, pady=5, sticky="w")
geometric_btn.grid(column=0, row=11, padx=5, pady=pady)
contraharm_btn.grid(column=1, row=11, padx=5, pady=pady)
ordstat_btn.grid(column=2, row=11, padx=5, pady=pady)
img_comp_label.grid(column=0, row=12, columnspan=3, pady=5, sticky="w")
rle_btn.grid(column=0, row=13, padx=5, pady=pady)
huffman_btn.grid(column=1, row=13, padx=5, pady=pady)

# setup metadata elements
metadata_title = ttk.Label(metadata_frame, text="Open an image first")
metadata_label = ttk.Label(metadata_frame, wraplength=170)
palette_title = ttk.Label(metadata_frame)
palette_image = ImageFrame(metadata_frame, closable=False)
metadata_title.pack(anchor="nw")
metadata_label.pack(anchor="nw", pady=(10, 25))
palette_title.pack(anchor="nw")

# setup keyboard shortcuts
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-O>", lambda event: open_file())

# start app
root.mainloop()

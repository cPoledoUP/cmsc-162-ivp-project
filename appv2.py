import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.custom_tk_widgets import ToolTipButton
from utils.button_icon_gen import IvpBtnIcon

# setup the root of the app
root = tk.Tk()
root.title("Image Processing App")
root.geometry("1280x720")
root.state("zoomed")

# configure styling
# ttk.Style().configure("TFrame", background="#121212")

# setup main frame
main_notebook = ttk.Notebook(root)
main_notebook.pack(side="left", fill="both", expand=True)

main_frame = ttk.Frame(main_notebook, relief="solid")
main_frame.pack(fill="both", expand=True)

main_notebook.add(main_frame, text="Original")

# setup sidebar frame
sidebar = ttk.Notebook(root, width=200)
sidebar.pack(side="right", fill="y")

buttons_frame = ttk.Frame(sidebar, relief="solid", padding=10)
buttons_frame.pack(fill="both", expand=True)
metadata_frame = ttk.Frame(sidebar, relief="solid")
metadata_frame.pack(fill="both", expand=True)

sidebar.add(buttons_frame, text="Edit")
sidebar.add(metadata_frame, text="Metadata")

# setup sidebar buttons
# color buttons
dark_btn_icon = IvpBtnIcon.black()
color_btn_label = ttk.Label(buttons_frame, text="Color Channels")
red_btn_icon = IvpBtnIcon.red()
red_btn = ToolTipButton(buttons_frame, image=red_btn_icon, tooltip="Red Channel")
green_btn_icon = IvpBtnIcon.green()
green_btn = ToolTipButton(buttons_frame, image=green_btn_icon, tooltip="Green Channel")
blue_btn_icon = IvpBtnIcon.blue()
blue_btn = ToolTipButton(buttons_frame, image=blue_btn_icon, tooltip="Blue Channel")
# image transform buttons
img_trans_label = ttk.Label(buttons_frame, text="Image Transformation")
gray_btn_icon = IvpBtnIcon.grayscale()
gray_btn = ToolTipButton(
    buttons_frame, image=gray_btn_icon, tooltip="Grayscale Transform"
)
neg_btn_icon = IvpBtnIcon.black()
neg_btn = ToolTipButton(
    buttons_frame, image=neg_btn_icon, tooltip="Negative Transform", text="+/-"
)
bnw_btn_icon = IvpBtnIcon.black_and_white()
bnw_btn = ToolTipButton(
    buttons_frame, image=bnw_btn_icon, tooltip="Black and White Transform"
)
gamma_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Gamma Transform", text="γ"
)
# spatial filter buttons
filter_label = ttk.Label(buttons_frame, text="Spatial Filtering")
ave_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Averaging Filter", text="x̄"
)
med_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Median Filter", text="x͂"
)
hipass_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Highpass Filter", text="HI"
)
unsharp_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Unsharp Masking", text="U"
)
hiboost_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Highboost Filter", text="HB"
)
gradient_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Image Gradient", text="G"
)
# image degradation buttons
img_deg_label = ttk.Label(buttons_frame, text="Image Degradation")
salt_pepper_btn_icon = IvpBtnIcon.salt_and_pepper()
salt_pepper_btn = ToolTipButton(
    buttons_frame, image=salt_pepper_btn_icon, tooltip="Salt and Pepper Noise"
)
gauss_btn_icon = IvpBtnIcon.gauss()
gauss_btn = ToolTipButton(buttons_frame, image=gauss_btn_icon, tooltip="Gaussian Noise")
erlang_btn_icon = IvpBtnIcon.erlang()
erlang_btn = ToolTipButton(buttons_frame, image=erlang_btn_icon, tooltip="Erlang Noise")
# image restoration buttons
img_res_label = ttk.Label(buttons_frame, text="Image Restoration")
geometric_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Geometric Mean Filter", text="Π"
)
contraharm_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Contraharmonic Mean Filter", text="Σ/Σ"
)
ordstat_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Order-Statistics Filter", text="x͂"
)
# image compression buttons
img_comp_label = ttk.Label(buttons_frame, text="Image Compression")
rle_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Run-length Encoding", text="RLE"
)
huffman_btn = ToolTipButton(
    buttons_frame, image=dark_btn_icon, tooltip="Huffman Coding", text="HC"
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

# start app
root.mainloop()

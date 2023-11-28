from PIL import Image, ImageTk
import random


class IvpBtnIcon:
    def red():
        return ImageTk.PhotoImage(Image.new("RGB", (30, 30), (255, 0, 0)))

    def green():
        return ImageTk.PhotoImage(Image.new("RGB", (30, 30), (0, 255, 0)))

    def blue():
        return ImageTk.PhotoImage(Image.new("RGB", (30, 30), (0, 0, 255)))

    def grayscale():
        return ImageTk.PhotoImage(Image.new("L", (30, 30), 127))

    def black_and_white():
        img = Image.new("L", (30, 30))
        # put the black part
        pixel_data = list()
        blk_count = 30
        for h in range(30):
            for w in range(30):
                if w < blk_count:
                    pixel_data.append(0)
                else:
                    pixel_data.append(255)
            blk_count -= 1
        img.putdata(pixel_data)

        return ImageTk.PhotoImage(img)

    def salt_and_pepper():
        random.seed(42069)
        img = Image.new("L", (30, 30), 127)
        for i in range(20):
            img.putpixel((random.randint(0, 29), random.randint(0, 29)), 0)
            img.putpixel((random.randint(0, 29), random.randint(0, 29)), 255)

        return ImageTk.PhotoImage(img)

    def gauss():
        random.seed(42069)
        img = Image.new("L", (30, 30))
        pixel_data = [random.gauss(127, 20) for i in range(900)]
        img.putdata(pixel_data)

        return ImageTk.PhotoImage(img)

    def erlang():
        random.seed(42069)
        img = Image.new("L", (30, 30))
        pixel_data = [127 + random.gammavariate(1, 20) for i in range(900)]
        img.putdata(pixel_data)

        return ImageTk.PhotoImage(img)

    def dark():
        return ImageTk.PhotoImage(Image.new("L", (30, 30), 50))

    def black():
        return ImageTk.PhotoImage(Image.new("L", (30, 30), 0))

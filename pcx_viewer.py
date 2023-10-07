from PIL import Image, ImageDraw

class PcxImage:

    def __init__(self, location):
        pcx_file = open(location, mode='br')
        
        self.location = location.split('/')[-1]
        self.manufacturer = pcx_file.read(1)
        self.version = pcx_file.read(1)
        self.encoding = pcx_file.read(1)
        self.bits_per_pixel = pcx_file.read(1)
        self.window = pcx_file.read(8)
        self.hdpi = pcx_file.read(2)
        self.vdpi = pcx_file.read(2)
        self.color_map = pcx_file.read(48)
        self.reserved = pcx_file.read(1)
        self.n_planes = pcx_file.read(1)
        self.bytes_per_line = pcx_file.read(2)
        self.palette_info = pcx_file.read(2)
        self.h_screen_size = pcx_file.read(2)
        self.v_screen_size = pcx_file.read(2)
        self.filler = pcx_file.read(54)
        self.image_buffer = pcx_file.read()
        
        pcx_file.close()
    
    def get_manufacturer(self):
        match self.manufacturer[0]:
            case 10:
                return 'Zshoft .pcx (10)'
            case _:
                return 'Unknown manufacturer'
    
    def get_version(self):
        return self.version[0]
        # match self.version[0]:
        #     case 0:
        #         return 'Ver. 2.5 of PC Paintbrush'
        #     case 2:
        #         return 'Ver. 2.8 w/palette information'
        #     case 3:
        #         return 'Ver. 2.8 w/o palette information'
        #     case 4:
        #         return 'PC Paintbrush for Windows(Plus for Windows uses Ver 5)'
        #     case 5:
        #         return 'Ver. 3.0 and > of PC Paintbrush and PC Paintbrush +, includes Publisher’s Paintbrush. Includes 24 bit .PCX files'
        #     case _:
        #         return 'Unknown version'
    
    def get_encoding(self):
        return self.encoding[0]
        # match self.encoding[0]:
        #     case 0:
        #         return 'No encoding'
        #     case 1:
        #         return '.PCX run length encoding'
        #     case _:
        #         return 'Unknown encoding'
    
    def get_bits_per_pixel(self):
        return self.bits_per_pixel[0]
    
    def get_window(self):
        first_val = 0
        values = list()
        for i, byte in enumerate(self.window):
            if i % 2 == 1:
                left_side = byte << 8
                values.append(left_side + first_val)
            else:
                first_val = byte
                
        return values

    def get_hdpi(self):
        left_side = self.hdpi[1] << 8
        return left_side + self.hdpi[0]

    def get_vdpi(self):
        left_side = self.vdpi[1] << 8
        return left_side + self.vdpi[0]
    
    def get_color_map(self):
        palette = list()
        rgb = list()
        for i, byte in enumerate(self.color_map):
            rgb.append(byte)
            if i % 3 == 2:
                palette.append(rgb)
                rgb = list()
        return palette

    def get_reserved(self):
        return self.reserved[0]
    
    def get_n_planes(self):
        return self.n_planes[0]
    
    def get_bytes_per_line(self):
        left_side = self.bytes_per_line[1] << 8
        return left_side + self.bytes_per_line[0]
    
    def get_palette_info(self):
        left_side = self.palette_info[1] << 8
        return left_side + self.palette_info[0]
        # match left_side + self.palette_info[0]:
        #     case 1:
        #         return 'Color.BW'
        #     case 2:
        #         return 'Grayscale (ignored in PB IV/IV+)'
        #     case _:
        #         return 'Unknown palette info'
            
    def get_h_screen_size(self):
        left_side = self.h_screen_size[1] << 8
        return left_side + self.h_screen_size[0]
    
    def get_v_screen_size(self):
        left_side = self.v_screen_size[1] << 8
        return left_side + self.v_screen_size[0]
    
    def get_filler(self):
        return self.filler

    def get_palette_data(self):
        palette_bytes = list()
        palette = list()
        if self.get_version() == 5 and self.image_buffer[-769] == 12:
            # get last 768 bytes
            palette_bytes = self.image_buffer[-768:]
            rgb = list()
            for i in range(768):
                rgb.append(palette_bytes[i])
                if i % 3 == 2:
                    palette.append(tuple(rgb))
                    rgb = list()
  
        return palette
    
    def get_image_palette(self, pixel_length):
        rgb_values = self.get_palette_data()
         
        target_size = 16
        
        image = Image.new(mode="RGB", size=(target_size*pixel_length, target_size*pixel_length))

        if len(rgb_values) == 0:
            return image
        
        draw = ImageDraw.Draw(image)
    
        for y in range (target_size): 
            for x in range (target_size):
                draw.rectangle([x * pixel_length,y * pixel_length, x * pixel_length + pixel_length, y * pixel_length + pixel_length], fill=rgb_values[y*target_size+x])  
                      
        return image
    
    def get_image_data(self):
        # https://people.sc.fsu.edu/~jburkardt/txt/pcx_format.txt

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1
        total_bytes = self.get_n_planes() * self.get_bytes_per_line()

        image_buffer = self.image_buffer
        image_data = list()

        if self.get_version() == 5 and image_buffer[-769] == 12:
            image_buffer = image_buffer[:-769]

        line_count = 0
        line_buffer = list()
        force_write_color = False

        for byte in image_buffer:
            if force_write_color:
                for i in range(count):
                    line_count += 1
                    line_buffer.append(byte)
                count = 0
                force_write_color = False
            elif byte & 192 == 192: # check if top 2 bits are set (and to 11000000 then check if the result is 11000000)
                # return lower 6 bits (and to 00111111)
                count = byte & 63
                force_write_color = True
            else:
                line_count += 1
                line_buffer.append(byte)
            
            if line_count >= total_bytes:
                image_data.append(line_buffer)
                line_buffer = list()
                line_count = 0
        
        return image_data
    
    def get_image(self):
        palette = self.get_palette_data()
        img_data = self.get_image_data()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        disp_img = Image.new('RGB', (width, height))

        if len(palette) != 0:   # palette at eof exist, use that
            for y, list in enumerate(img_data):
                for x, pix in enumerate(list):
                    disp_img.putpixel((x, y), palette[pix])
        elif self.get_bits_per_pixel() == 1 and self.get_n_planes() == 1:   # monochrome
            for y, list in enumerate(img_data):
                for x, pix in enumerate(list):
                    for i, bit in enumerate(bin(pix)[2:]):  # 1 bit per pixel, pix is 8 bits (1 byte)
                        color = int(bit) * 255
                        disp_img.putpixel((x * 8 + i, y), (color, color, color))
        elif self.get_bits_per_pixel() == 8 and self.get_n_planes() == 3:   # not using palette (16.7 mil color)
            for y, list in enumerate(img_data):
                row_len = len(list)
                color_size = int(row_len / 3)
                r = list[:color_size]
                g = list[color_size: color_size*2]
                b = list[color_size*2: color_size*3]
                for x in range(color_size):
                    disp_img.putpixel((x, y), (r[x], g[x], b[x]))

        return disp_img

    ########## Project 1 Guide 3 ##########

    def get_color_channels(self):
        red = []
        green = []
        blue = []

        pixel_data = self.get_image_data()
        color_palette = self.get_palette_data()

        for list in pixel_data:
            for index in list:
                red.append(color_palette[index][0])
                green.append(color_palette[index][1])
                blue.append(color_palette[index][2])
        
        return {
            'red': red,
            'green': green,
            'blue': blue
        }
    
    def show_color_channel_images(self, color):
        color_data = self.get_color_channels()[color]
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for i in range(len(color_data)):
            if color == 'red':
                color_data[i] = (color_data[i], 0, 0)
            elif color == 'green':
                color_data[i] = (0, color_data[i], 0)
            elif color == 'blue':
                color_data[i] = (0, 0, color_data[i])

        disp_img = Image.new('RGB', (width, height))

        for y in range(height):
            for x in range(width):
                disp_img.putpixel((x, y), color_data[y * width + x])
        
        return disp_img
    
    ########## Project 1 Guide 4 ##########

    def get_grayscale_image(self, mode = 'image'):
        # mode must be either 'image' or 'values'
        # if image -> returns a displayable image
        # if values -> returns an array of pixel values
        
        palette = self.get_palette_data()
        image_data = self.get_image_data()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        grayscale_image_data = list()

        # get average of values to create new pixel data
        for y in range(height):
            for x in range(width):
                rgb_values = palette[image_data[y][x]]
                grayscale_image_data.append(int((rgb_values[0] + rgb_values[1] + rgb_values[2]) / 3))
        
        if mode == 'values':
            return grayscale_image_data
        elif mode == 'image':
            disp_img = Image.new('L', (width, height))
            disp_img.putdata(grayscale_image_data)
            return disp_img
        else:
            return -1
    
    def get_negative_image(self):
        grayscale_image_data = self.get_grayscale_image('values')
        negative_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in grayscale_image_data:
            negative_image_data.append(255 - pixel)
        
        disp_img = Image.new('L', (width, height))
        disp_img.putdata(negative_image_data)

        return disp_img

    def get_black_and_white_image(self, threshold):
        grayscale_image_data = self.get_grayscale_image('values')
        bnw_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in grayscale_image_data:
            if pixel > threshold:
                bnw_image_data.append(1)
            else:
                bnw_image_data.append(0)
        
        disp_img = Image.new('1', (width, height))
        disp_img.putdata(bnw_image_data)

        return disp_img
    
    def get_gamma_tranformed_image(self, gamma):
        grayscale_image_data = self.get_grayscale_image('values')
        gamma_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in grayscale_image_data:
            c = 1   # based on slides
            gamma_image_data.append(c * (pixel ** gamma))
        
        disp_img = Image.new('L', (width, height))
        disp_img.putdata(gamma_image_data)

        return disp_img


PcxImage('scene1.pcx').get_gamma_tranformed_image(1.1).show()
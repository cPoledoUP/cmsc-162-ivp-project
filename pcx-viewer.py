# from PIL import Image
# import numpy as np

class PcxImage:

    def __init__(self, location):
        pcx_file = open(location, mode='br')

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

    # def get_image_buffer(self):
    #     # https://people.sc.fsu.edu/~jburkardt/txt/pcx_format.txt
    #     window = self.get_window()
    #     width = window[2] - window[0] + 1
    #     height = window[3] - window[1] + 1
    #     bytes_per_line = self.get_bytes_per_line()
    #     n_planes = self.get_n_planes()
    #     scan_line_size = n_planes * bytes_per_line

    #     image_buffer = list()
    #     line_buffer = list()
    #     plane_buffer = list()

    #     current_line_count = 0
    #     current_plane_count = 0
    #     count = 0
    #     current_height = 0
    #     image_end_index = 0

    #     for i, byte in enumerate(self.image_buffer):
    #         print(i)
    #         if current_height >= height:
    #             image_end_index = i
    #             break

    #         # check if top 2 bits are set (and to 11000000 or 192 then check if the result is 11000000 or 192)
    #         if byte & 192 == 192:
    #             # return lower 6 bits (and to 00111111 or 63)
    #             count = byte & 63
    #         else:
    #             if count == 0:
    #                 current_line_count += 1
    #                 current_plane_count += 1
    #                 plane_buffer.append(byte)
    #             else:
    #                 for i in range(count):
    #                     current_line_count += 1
    #                     current_plane_count += 1
    #                     plane_buffer.append(byte)
    #                 count = 0
            
    #         if current_plane_count >= n_planes:
    #             line_buffer.append(plane_buffer)
    #             current_plane_count = 0
            
    #         if current_line_count >= scan_line_size:
    #             image_buffer.append(line_buffer)
    #             current_line_count = 0
    #             current_height += 1
        
    #     return image_buffer
    
    # def create_image(self):
    #     window = self.get_window()
    #     width = window[2] - window[0] + 1
    #     height = window[3] - window[1] + 1
    #     image_buffer = self.get_image_buffer()
    #     line = list()
    #     image = list()
    #     for i, pix in enumerate(image_buffer):
    #         line.append(pix)
    #         if i % width == width - 1:
    #             image.append(line)
    #             line = list()
        
    #     return np.array(image)

    def get_palette_data(self):
        palette_bytes = list()
        palette = list()
        if self.get_version() == 5:
            # get last 768 bytes
            palette_bytes = self.image_buffer[-768:]
            rgb = list()
            for i in range(768):
                rgb.append(palette_bytes[i])
                if i % 3 == 2:
                    palette.append(rgb)
                    rgb = list()

        
        return palette

# img = PcxImage('sample_640×426.pcx')
# img2 = PcxImage('bunny.pcx')
# print(img2.get_image_buffer())
# print(img2.get_image())
# print(PcxImage('scene1.pcx').get_palette_data())

# image = img.create_image()
# im = Image.fromarray(image)
# im.show()
from PIL import Image, ImageDraw
import numpy as np
class PcxImage:

    def __init__(self, location: str) -> None:
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

        self.image_data = None
        self.eof_palette = None

        self.grayscale_image_data = None
        
        pcx_file.close()
    
    def get_manufacturer(self) -> str:
        """
        Returns the manufacturer of the pcx file

        Returns
        -------
        str
            mostly 'Zshoft .pcx (10)'
        """

        match self.manufacturer[0]:
            case 10:
                return 'Zshoft .pcx (10)'
            case _:
                return 'Unknown manufacturer'
    
    def get_version(self) -> int:
        """
        Returns the version number of the pcx file

        Returns
        -------
        int
            version number
        """

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
    
    def get_encoding(self) -> int:
        """
        Returns the encoding of the pcx file

        Returns
        -------
        int
            encoding
        """

        return self.encoding[0]
        # match self.encoding[0]:
        #     case 0:
        #         return 'No encoding'
        #     case 1:
        #         return '.PCX run length encoding'
        #     case _:
        #         return 'Unknown encoding'
    
    def get_bits_per_pixel(self) -> int:
        """
        Returns the bits per pixel of the pcx file

        Returns
        -------
        int
            bits per pixel
        """
        
        return self.bits_per_pixel[0]
    
    def get_window(self) -> list:
        """
        Returns the window of the pcx file

        Returns
        -------
        list
            [x_min, y_min, x_max, y_max]
        """
        
        first_val = 0
        values = list()
        for i, byte in enumerate(self.window):
            if i % 2 == 1:
                left_side = byte << 8
                values.append(left_side + first_val)
            else:
                first_val = byte
                
        return values

    def get_hdpi(self) -> int:
        """
        Returns the hdpi of the pcx file

        Returns
        -------
        int
            hdpi
        """
        
        left_side = self.hdpi[1] << 8
        return left_side + self.hdpi[0]

    def get_vdpi(self) -> int:
        """
        Returns the vdpi of the pcx file

        Returns
        -------
        int
            vdpi
        """
        
        left_side = self.vdpi[1] << 8
        return left_side + self.vdpi[0]
    
    def get_color_map(self) -> list:
        """
        Returns the header palette of the pcx file

        Returns
        -------
        list
            [(r, g, b), (r, g, b), ...]
        """
        
        palette = list()
        rgb = list()
        for i, byte in enumerate(self.color_map):
            rgb.append(byte)
            if i % 3 == 2:
                palette.append(rgb)
                rgb = list()
        return palette

    def get_reserved(self) -> int:
        """
        Returns the reserved bits of the pcx file

        Returns
        -------
        int
            should be 0
        """
        
        return self.reserved[0]
    
    def get_n_planes(self) -> int:
        """
        Returns the number of planes of the pcx file

        Returns
        -------
        int
            number of planes
        """
        
        return self.n_planes[0]
    
    def get_bytes_per_line(self) -> int:
        """
        Returns the bytes per line of the pcx file

        Returns
        -------
        int
            bytes per line
        """
        
        left_side = self.bytes_per_line[1] << 8
        return left_side + self.bytes_per_line[0]
    
    def get_palette_info(self) -> int:
        """
        Returns the palette info of the pcx file

        Returns
        -------
        int
            palette info
        """
        
        left_side = self.palette_info[1] << 8
        return left_side + self.palette_info[0]
        # match left_side + self.palette_info[0]:
        #     case 1:
        #         return 'Color.BW'
        #     case 2:
        #         return 'Grayscale (ignored in PB IV/IV+)'
        #     case _:
        #         return 'Unknown palette info'
            
    def get_h_screen_size(self) -> int:
        """
        Returns the horizontal screen size of the pcx file

        Returns
        -------
        int
            horizontal screen size
        """
        
        left_side = self.h_screen_size[1] << 8
        return left_side + self.h_screen_size[0]
    
    def get_v_screen_size(self) -> int:
        """
        Returns the vertical screen size of the pcx file

        Returns
        -------
        int
            vertical screen size
        """
        
        left_side = self.v_screen_size[1] << 8
        return left_side + self.v_screen_size[0]
    
    def get_filler(self) -> bytes:
        """
        Returns the filler bytes of the pcx file

        Returns
        -------
        bytes
            filler bytes, should be 0
        """
        
        return self.filler
    
    def process_image_data(self) -> None:
        """
        Processes the image data (and possible eof palette) of the pcx file

        Raises
        ------
        Exception
            if inputted image is not an rgb image
        """
        
        # https://people.sc.fsu.edu/~jburkardt/txt/pcx_format.txt
        # http://www.fysnet.net/pcxfile.htm

        dimensions = self.get_window()
        height = dimensions[3] - dimensions[1] + 1
        n_planes = self.get_n_planes()
        bytes_per_line = self.get_bytes_per_line()
        total_bytes = n_planes * bytes_per_line

        image_buffer = self.image_buffer
        image_data = list()

        index = 0
        current_line_bytes = 0
        current_lines = 0

        while index < len(image_buffer):

            # track how many lines are written
            if current_line_bytes >= total_bytes:
                current_line_bytes = 0
                current_lines += 1
            
            # stop if all image data is read
            if current_lines == height:
                break

            if image_buffer[index] & 192 == 192:    # if top 2 bits are set
                count = image_buffer[index] & 63    # lower 6 bits as count
                current_line_bytes += count
                for x in range(count):
                    image_data.append(image_buffer[index + 1])
                index += 2
            else:
                image_data.append(image_buffer[index])
                current_line_bytes += 1
                index += 1
        
        palette = list()
        rgb_image_data = list()

        if index < len(image_buffer):   # eof palette exist
            image_buffer = image_buffer[-768:]
        
            palette = [(image_buffer[i], image_buffer[i + 1], image_buffer[i + 2]) for i in range(0, len(image_buffer), 3)]
            
            for j in range(len(image_data)):
                rgb_image_data.append(palette[image_data[j]])
        elif self.get_bits_per_pixel() == 8 and n_planes == 3:
            # convert list of data into an rgb tuple
            for i in range(0, len(image_data), total_bytes):
                for j in range(i, i + int(total_bytes / n_planes)):
                    color_tuple = list()
                    offset = 0
                    for k in range(n_planes):
                        color_tuple.append(image_data[j + offset])
                        offset += bytes_per_line
                    rgb_image_data.append(tuple(color_tuple))
        else:
            raise Exception("Error opening the pcx file. App only supports opening rgb images.")
                
        self.image_data = rgb_image_data
        self.eof_palette = palette
    
    def get_image_palette(self, pixel_length: int) -> Image:
        """
        Returns the image palette of the pcx file as displayable image

        Parameters
        ----------
        pixel_length : int
            pixel dimension of a single color in the palette

        Returns
        -------
        Image
            image of eof palette
        """
        if self.eof_palette == None:
            self.process_image_data()
         
        target_size = 16
        
        image = Image.new(mode="RGB", size=(target_size*pixel_length, target_size*pixel_length), color='#B0B0B0')

        if len(self.eof_palette) == 0:
            return image
        
        draw = ImageDraw.Draw(image)
    
        for y in range (target_size): 
            for x in range (target_size):
                draw.rectangle([x * pixel_length,y * pixel_length, x * pixel_length + pixel_length, y * pixel_length + pixel_length], fill=self.eof_palette[y*target_size+x])  
                      
        return image
    
    def get_image(self) -> Image:
        """
        Returns pcx image as a displayable image

        Returns
        -------
        Image
            displayable pcx image
        """
        if self.image_data == None:
            self.process_image_data()
        
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        disp_img = Image.new('RGB', (width, height))
        disp_img.putdata(self.image_data)

        return disp_img

    ########## Project 1 Guide 3 ##########

    def get_color_channels(self) -> dict:
        """
        Returns the color channels of the eof palette

        Returns
        -------
        dict
            {'red': list, 'green': list, 'blue': list}
        """
        if self.image_data == None:
            self.process_image_data()
        
        red = []
        green = []
        blue = []

        for pixel in self.image_data:
            red.append(pixel[0])
            green.append(pixel[1])
            blue.append(pixel[2])
        
        return {
            'red': red,
            'green': green,
            'blue': blue
        }
    
    def show_color_channel_images(self, color: str) -> Image:
        """
        Returns a color channel of the pcx image as displayable image

        Parameters
        ----------
        color : str
            'red', 'green', 'blue'

        Returns
        -------
        Image
            pcx image using only one color channel
        """
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
    def process_grayscale_image_data(self) -> None:
        """
        Processes and stores a list of the data of the grayscale image to prevent repetition of calculation
        """
        if self.image_data == None:
            self.process_image_data()
            
        self.grayscale_image_data = list()
        for pixel in self.image_data:
            self.grayscale_image_data.append(int((pixel[0] + pixel[1] + pixel[2]) / 3))

    def get_grayscale_image(self) -> Image:
        """
        Returns a grayscale transformed version of the pcx image as a displayable image

        Returns
        -------
        Image
            a grayscale image
        """
        
        # get average of values to create new pixel data
        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        disp_img = Image.new('L', (width, height))
        disp_img.putdata(self.grayscale_image_data)
        return disp_img
    
    def get_negative_image(self) -> Image:
        """
        Returns a negative transformed version of the pcx image as a displayable image

        Returns
        -------
        Image
            a negative transformed pcx image
        """

        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()

        negative_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in self.grayscale_image_data:
            negative_image_data.append(255 - pixel)
        
        disp_img = Image.new('L', (width, height))
        disp_img.putdata(negative_image_data)

        return disp_img

    def get_black_and_white_image(self, threshold: int) -> Image:
        """
        Returns a black and white transformed version of the pcx image as a displayable image

        Parameters
        ----------
        threshold : int
            range of [0, 255], threshold to determine white and black pixels

        Returns
        -------
        Image
            a black and white transformed pcx image
        """

        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()
        
        bnw_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in self.grayscale_image_data:
            if pixel > threshold:
                bnw_image_data.append(255)
            else:
                bnw_image_data.append(0)
        
        disp_img = Image.new('L', (width, height))
        disp_img.putdata(bnw_image_data)

        return disp_img
    
    def get_gamma_transformed_image(self, gamma: float) -> Image:
        """
        Returns a black and white transformed version of the pcx image as a displayable image

        Parameters
        ----------
        gamma : float
            a positive floating point value for gamma transform

        Returns
        -------
        Image
            a gamma transformed pcx image
        """

        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()
        
        gamma_image_data = list()
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        for pixel in self.grayscale_image_data:
            c = 1   # based on slides
            gamma_image_data.append(c * (pixel ** gamma))
        
        disp_img = Image.new('L', (width, height))
        disp_img.putdata(gamma_image_data)

        return disp_img

    def get_averaging_filter (self, radius=1):
        """ Function to get the average-filtered (blur) image
        
        Parameters:
        ------------
        radius : integer
            number of pixels away from each coordinate to be used in the function
            
        Returns:
        ------------
        Image : 
            An average-filtered image (blurred)
            
        """
        
        if self.grayscale_image_data == None:
            self.process_grayscale_image_data() # uses the grayscale-filtered version of the image
        
        filtered_image = self.grayscale_image_data
        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1
        two_d_list = [] # store the 2-dimensional array converted version of the grayscale_image_data
        
        for x in range(0, len(filtered_image), width):
            two_d_list.append(filtered_image[x: x + width])
        
        new_image = [] # stores the calculated values of the average-filtered image
        
        for y in range(height): # rows
            for x in range(width): # columns
                new_image.append(self.get_mean_square(two_d_list, y, x, radius))

        disp_img = Image.new('L', (width, height))
        disp_img.putdata(new_image)
        
        return disp_img
        
    def get_mean_square (self, matrix, row, col, radius):
        """Function to calculate the mean using the neighbouring values of a given coordinate in a matrix

        Parameters:
        --------------
        matrix (2dim array of integers): 
            the grayscale image converted to a 2 dimensional matrix
            
        row (integer): 
            The row coordinate of the element
            
        col (integer): 
            The column coordinate of the element
            
        radius (integer): 
            The number of neighbours the function uses

        Returns:
        --------------
        mean (integer): 
            Calculated mean from the neighbouring values n-units away (radius) from the coordinate
             
        """
    
        neighbors = []  # Define relative positions for neighbors according to the radius
        for y in range(row-radius, row+radius):
            for x in range(col-radius, col+radius):
                neighbors.append((y,x))
            
        neighbor_list = []  # Stores the values of each neighbour coordinate

        
        for r, c in neighbors:  # Check if each neighbor is within the bounds of the matrix
            if 0 <= r < len(matrix) and 0 <= c < len(matrix[0]):
                neighbor_list.append(matrix[r][c])
                
        mean = 0 # Initialize the mean value
        
        for i in range(0, len(neighbor_list)):
            neighbor_list[i] = int(neighbor_list[i])
            mean = mean + neighbor_list[i]
        
        mean = mean/len(neighbor_list)
        
        return mean
    
if __name__ == '__main__':
    img = PcxImage('1.pcx')
    img.get_averaging_filter().show()
    
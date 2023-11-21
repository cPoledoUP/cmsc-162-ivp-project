from PIL import Image, ImageDraw


class PcxImage:
    def __init__(self, location: str) -> None:
        pcx_file = open(location, mode="br")

        self.location = location.split("/")[-1]
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
                return "Zshoft .pcx (10)"
            case _:
                return "Unknown manufacturer"

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

            if image_buffer[index] & 192 == 192:  # if top 2 bits are set
                count = image_buffer[index] & 63  # lower 6 bits as count
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

        if index < len(image_buffer):  # eof palette exist
            image_buffer = image_buffer[-768:]

            palette = [
                (image_buffer[i], image_buffer[i + 1], image_buffer[i + 2])
                for i in range(0, len(image_buffer), 3)
            ]

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
            raise Exception(
                "Error opening the pcx file. App only supports opening rgb images."
            )

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

        image = Image.new(
            mode="RGB",
            size=(target_size * pixel_length, target_size * pixel_length),
            color="#B0B0B0",
        )

        if len(self.eof_palette) == 0:
            return image

        draw = ImageDraw.Draw(image)

        for y in range(target_size):
            for x in range(target_size):
                draw.rectangle(
                    [
                        x * pixel_length,
                        y * pixel_length,
                        x * pixel_length + pixel_length,
                        y * pixel_length + pixel_length,
                    ],
                    fill=self.eof_palette[y * target_size + x],
                )

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

        disp_img = Image.new("RGB", (width, height))
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

        return {"red": red, "green": green, "blue": blue}

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
            if color == "red":
                color_data[i] = (color_data[i], 0, 0)
            elif color == "green":
                color_data[i] = (0, color_data[i], 0)
            elif color == "blue":
                color_data[i] = (0, 0, color_data[i])

        disp_img = Image.new("RGB", (width, height))

        for y in range(height):
            for x in range(width):
                disp_img.putpixel((x, y), color_data[y * width + x])

        return disp_img

    ########## Project 1 Guide 4 ##########
    def process_grayscale_image_data(self) -> None:
        """
        Processes and stores a list of the data of the grayscale image to prevent repetition of calculation
        s = (R + G + B) / 3
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

        disp_img = Image.new("L", (width, height))
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

        disp_img = Image.new("L", (width, height))
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

        disp_img = Image.new("L", (width, height))
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
            c = 255  # scaling constant
            gamma_image_data.append(c * ((pixel / c) ** gamma))

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(gamma_image_data)

        return disp_img

    ########## Project 1 Guide 5 ##########

    # Helper functions
    def get_neighbors(self, coordinates: tuple, radius: int = 1, pad: int = 0) -> list:
        """
        Returns the neighboring pixels of a given pixel coordinate

        Parameters:
        -----------
        coordinates : tuple
            coordinates of the pixel as (x, y)
        radius : int
            radius of the neighboring area to get (default: 1 (or 3x3 area))
        pad : int
            value for out of bounds pixels (default: 0)

        Returns:
        --------
        list
            the neighboring pixels as a list
        """

        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        neighbors = list()
        # traverse each pixel starting from the upper-left to the lower-right pixels
        for y in range(coordinates[1] - radius, coordinates[1] + radius + 1):
            for x in range(coordinates[0] - radius, coordinates[0] + radius + 1):
                if (
                    x < 0 or x >= width or y < 0 or y >= height
                ):  # if out of bounds index
                    neighbors.append(pad)
                else:
                    neighbors.append(self.grayscale_image_data[y * width + x])

        return neighbors

    # Image functions
    def get_average_filtered_image(self, radius: int = 1) -> Image:
        """
        Function to get the average-filtered (blur) image

        Parameters:
        ------------
        radius : int
            number of pixels away from each coordinate to be used in the function (mask size)

        Returns:
        ------------
        Image
            An average-filtered image (blurred)

        """

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        filtered_image = (
            []
        )  # stores the calculated values of the average-filtered image

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors((x, y), radius)
                filtered_image.append(int(sum(neighbors) / len(neighbors)))

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_median_filtered_image(self, radius: int = 1) -> Image:
        """
        Creates an median-filtered version of a grayscale version of an image

        Parameters
        ----------
        radius : int
            Determines the mask size to be used in the filter

        Returns
        -------
        Image
            median-filtered grayscale image
        """

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        filtered_image = []

        middle_index = int(((2 * radius + 1) ** 2) / 2)
        # 2*radius+1 is side of mask, square and you get the area or total number of pixels in mask
        # divide by 2, and getting the floor, you get the middle index (no need +1 since index starts from 0)
        # (optimization) this is calculated once here instead of everytime in the for loop below

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors((x, y), radius)
                neighbors.sort()
                filtered_image.append(
                    neighbors[middle_index]
                )  # median is middle index of sorted list

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_highpass_filtered_image(self, filter: int = 1) -> Image:
        """
        Returns a laplacian transformed version of the image

        Parameters
        ----------
        filter : int
            Used to determine which of the available filters to use

        Returns
        -------
        Image
            Laplacian transformed image
        """

        # check which filter to use
        match filter:
            case 1:
                filter_used = [
                    0,
                    1,
                    0,
                    1,
                    -4,
                    1,
                    0,
                    1,
                    0,
                ]  # First filter where the center value is negative 4
            case 2:
                filter_used = [
                    0,
                    -1,
                    0,
                    -1,
                    4,
                    -1,
                    0,
                    -1,
                    0,
                ]  # Second filter. Positive counterpart to the first one
            case 3:
                filter_used = [
                    1,
                    1,
                    1,
                    1,
                    -8,
                    1,
                    1,
                    1,
                    1,
                ]  # Third filter where the center value is negative 8
            case 4:
                filter_used = [
                    -1,
                    -1,
                    -1,
                    -1,
                    8,
                    -1,
                    -1,
                    -1,
                    -1,
                ]  # Fourth filter. Positive counterpart to the first one
            case _:
                filter_used = [
                    0,
                    1,
                    0,
                    1,
                    -4,
                    1,
                    0,
                    1,
                    0,
                ]  # Default filter: first filter

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        filtered_image = (
            []
        )  # stores the calculated values of the average-filtered image

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors((x, y))  # using default 3x3 mask
                filtered_image.append(
                    sum(
                        [neighbors[i] * filter_used[i] for i in range(len(filter_used))]
                    )
                )

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_unsharp_masked_image(self) -> Image:
        """
        Unsharps (sharpens) an image using the formula
        Unsharped_image = Grayscale_image + k * (Grayscale_image - average_filtered_image())

        Returns
        -------
        Image
            The Unsharped image
        """
        if self.grayscale_image_data == None:
            self.process_grayscale_image_data()

        blurred_image = list(self.get_average_filtered_image().getdata())
        original_image = self.grayscale_image_data
        # mask is subtracting the blurred image from the original image
        mask = [
            original_image[i] - blurred_image[i] for i in range(len(original_image))
        ]

        k = 1  # for unsharp masking
        unsharped_image = [
            original_image[i] + k * mask[i] for i in range(len(original_image))
        ]  # apply the mask on all pixels

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(unsharped_image)

        return disp_img

    def get_highboost_filtered_image(self, A: float = 1) -> Image:
        """
        returns a highboost filtered version of the image using the formula:
        highboosted_image = (A-1)Original + Highpass(1) where A is the intensity

        Parameters
        ----------
        A : float
            determines the intensity of the highboost filter to be applied

        Returns
        -------
        Image
            highboost filtered version of the image
        """

        highpassed_image = list(
            self.get_highpass_filtered_image(2).getdata()
        )  # store the highpassed version of the image using the second filter
        original_image = self.grayscale_image_data  # apply the function for each
        highboosted_image = [
            (A - 1) * original_image[i] + highpassed_image[i]
            for i in range(len(original_image))
        ]

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(highboosted_image)

        return disp_img

    def get_image_gradient(self, mode: int = 1) -> Image:
        """
        Returns an image processed with Sobel operator

        Parameters
        ----------
        mode : int
            1 for combined, 2 for x, 3 for y

        Returns
        -------
        Image
            image processed with sobel operator
        """

        sobel_operator_x = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
        sobel_operator_y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
        height = dimensions[3] - dimensions[1] + 1

        x_gradient = []  # stores the calculated values of the x gradient
        y_gradient = []  # stores the calculated values of the y gradient

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors((x, y))  # using default 3x3 mask
                if mode != 3:
                    x_gradient.append(
                        sum(
                            [
                                neighbors[i] * sobel_operator_x[i]
                                for i in range(len(sobel_operator_x))
                            ]
                        )
                    )
                if mode != 2:
                    y_gradient.append(
                        sum(
                            [
                                neighbors[i] * sobel_operator_y[i]
                                for i in range(len(sobel_operator_y))
                            ]
                        )
                    )

        if mode == 2:
            gradient_data = x_gradient
        elif mode == 3:
            gradient_data = y_gradient
        else:
            gradient_data = [
                abs(x_gradient[i]) + abs(y_gradient[i]) for i in range(len(x_gradient))
            ]

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(gradient_data)
        # disp_img.putdata([(x_gradient[i] ** 2 + y_gradient[i] ** 2) ** 0.5 for i in range(len(x_gradient))])

        return disp_img


if __name__ == "__main__":
    img = PcxImage("wad.pcx")
    print(img.get_n_planes())
    # img.get_highboost_filtered_image(2).show()

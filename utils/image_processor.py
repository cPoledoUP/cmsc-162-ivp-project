from PIL import Image, ImageDraw, ImageTk

# from pcx_parser import PcxImage
import random
import numpy as np
from matplotlib import pyplot as plt


class ImageProcessor:
    def get_displayable_image(image_data: list, width: int, height: int):
        img = Image.new("RGB", (width, height))
        img.putdata(image_data)

        return img

    def get_displayable_palette(palette_data, pixel_length: int) -> Image:
        target_size = 16

        image = Image.new(
            mode="RGB", size=(target_size * pixel_length, target_size * pixel_length)
        )

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
                    fill=palette_data[y * target_size + x],
                )

        return image

    def show_color_channel_images(image_data, width, height, color: str) -> Image:
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
        color_data = []

        for pixel in image_data:
            match color:
                case "red":
                    color_data.append(pixel[0])
                case "green":
                    color_data.append(pixel[1])
                case "blue":
                    color_data.append(pixel[2])

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

    def get_grayscale_image(image_data, width, height) -> Image:
        """
        Returns a grayscale transformed version of the pcx image as a displayable image
        & the data of the grayscale transformed image

        Returns
        -------
        Image
            a grayscale image

        List
            data of the grayscale image
        """

        grayscale_image_data = list()

        for pixel in image_data:
            grayscale_image_data.append(int((pixel[0] + pixel[1] + pixel[2]) / 3))

        print(width, height)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(grayscale_image_data)

        return disp_img

    def get_negative_image(grayscale_data, width, height) -> Image:
        """
        Returns a negative transformed version of the pcx image as a displayable image

        Returns
        -------
        Image
            a negative transformed pcx image
        """

        negative_image_data = list()

        for pixel in grayscale_data:
            negative_image_data.append(255 - pixel)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(negative_image_data)

        return disp_img

    def get_black_and_white_image(
        grayscale_data, width, height, threshold: int
    ) -> Image:
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

        bnw_image_data = list()

        for pixel in grayscale_data:
            if pixel > threshold:
                bnw_image_data.append(255)
            else:
                bnw_image_data.append(0)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(bnw_image_data)

        return disp_img

    def get_gamma_transformed_image(
        grayscale_data, width, height, gamma: float
    ) -> Image:
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

        gamma_image_data = list()

        for pixel in grayscale_data:
            c = 255  # scaling constant
            gamma_image_data.append(c * ((pixel / c) ** gamma))

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(gamma_image_data)

        return disp_img

    def get_neighbors(
        self,
        grayscale_data,
        width,
        height,
        coordinates: tuple,
        radius: int = 1,
        pad: int = 0,
        noised_image=None,
    ) -> list:
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

        if noised_image != None:
            noised_list = noised_image
        else:
            noised_list = grayscale_data

        neighbors = list()
        # traverse each pixel starting from the upper-left to the lower-right pixels
        for y in range(coordinates[1] - radius, coordinates[1] + radius + 1):
            for x in range(coordinates[0] - radius, coordinates[0] + radius + 1):
                if (
                    x < 0 or x >= width or y < 0 or y >= height
                ):  # if out of bounds index
                    neighbors.append(pad)
                else:
                    neighbors.append(noised_list[y * width + x])

        return neighbors

    # Image functions
    def get_average_filtered_image(self, width, height, radius: int = 1) -> Image:
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

    def get_median_filtered_image(
        self, width, height, radius: int = 1, noised_image=None
    ) -> Image:
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

        if noised_image != None:
            noised_list = noised_image

        filtered_image = []

        middle_index = int(((2 * radius + 1) ** 2) / 2)
        # 2*radius+1 is side of mask, square and you get the area or total number of pixels in mask
        # divide by 2, and getting the floor, you get the middle index (no need +1 since index starts from 0)
        # (optimization) this is calculated once here instead of everytime in the for loop below

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors((x, y), radius, noised_image=noised_list)
                neighbors.sort()
                filtered_image.append(
                    neighbors[middle_index]
                )  # median is middle index of sorted list

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_highpass_filtered_image(self, width, height, filter: int = 1) -> Image:
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

    def get_unsharp_masked_image(self, grayscale_data, width, height) -> Image:
        """
        Unsharps (sharpens) an image using the formula
        Unsharped_image = Grayscale_image + k * (Grayscale_image - average_filtered_image())

        Returns
        -------
        Image
            The Unsharped image
        """

        blurred_image = list(self.get_average_filtered_image().getdata())
        original_image = grayscale_data
        # mask is subtracting the blurred image from the original image
        mask = [
            original_image[i] - blurred_image[i] for i in range(len(original_image))
        ]

        k = 1  # for unsharp masking
        unsharped_image = [
            original_image[i] + k * mask[i] for i in range(len(original_image))
        ]  # apply the mask on all pixels

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(unsharped_image)

        return disp_img

    def get_highboost_filtered_image(
        self, grayscale_data, width, height, A: float = 1
    ) -> Image:
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
        original_image = grayscale_data  # apply the function for each
        highboosted_image = [
            (A - 1) * original_image[i] + highpassed_image[i]
            for i in range(len(original_image))
        ]

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(highboosted_image)

        return disp_img

    def get_image_gradient(self, width, height, mode: int = 1) -> Image:
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

        return disp_img

    def apply_salt_pepper(grayscale_data, width, height, probability: float):
        """
        Applies salt and pepper noise to a grayscale equivalent of the image

        Args:
            salt_probability (float): probability of salt
            pepper_probability (float): probability of pepper

        Returns:
            _type_: image
        """

        salt_pepper_values = []

        for pixel in grayscale_data:
            a = random.random()

            if a < probability:
                salt_pepper_values.append(255)
            elif a < (2 * probability):
                salt_pepper_values.append(0)
            else:
                salt_pepper_values.append(pixel)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(salt_pepper_values)

        return disp_img

    def apply_gaussian(grayscale_data, width, height):
        """
        Applies Gaussian noise to a grayscale equivalent of the image

        Returns:
            _type_: Image
        """

        mean = 0  # responsible for the bell curved shape of the distribution
        var = 20  # controls the amount of noise | variance determines the spread of the noise values | ^ Variance = Noisier Image

        gaussian_values = []

        # creating and storing the noise applied values
        for pixel in grayscale_data:
            noise = np.random.normal(mean, var, size=None)
            gaussian_values.append(pixel + noise)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(gaussian_values)

        return disp_img

    def apply_erlang(grayscale_data, width, height):
        """
        Applies Gamma noise to a grayscale equivalent of the image

        Returns:
            _type_: Image
        """

        alpha = 2  # controls the shape of the noise distribution | amount of noise
        beta = 20  # Adjust the beta value to control the scale of the noise distribution (overall brightness of the image)

        erlang_values = []

        # creating and storing the noise applied values
        for pixel in grayscale_data:
            # noise =  np.random.normal(alpha, beta, size=None)
            noise = np.random.gamma(alpha, beta)
            erlang_values.append(pixel + noise)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(erlang_values)

        return disp_img

    def add_geometric_filter(self, width, height, noise_degraded_img):
        """
        performs geometric filter restoration technique to the noised image

        Args:
            noise_degraded_img ( Image ): noised image

        Returns:
            Image : restored image using Geometric filter
        """

        geometric_filtered_image = []

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors(
                    coordinates=(x, y), noised_image=noise_degraded_img
                )  # using default 3x3 mask

                total = 1
                for (
                    element
                ) in neighbors:  # Get the product of the all the neighbouring pixels
                    total = total * element

                geometric_filtered_image.append(
                    total ** (1 / 9)
                )  # raise the total product to 1/9

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(geometric_filtered_image)

        return disp_img

    def add_contraharmonic(self, width, height, noise_degraded_img, q: int = 1):
        """
        performs contraharmonic filter on a noised image

        Args:
            noise_degraded_img ( Image ): noised image
            q (int, optional): q parameter specifying the order of the filter .Defaults to 1.

        Returns:
            Image : restored image using Contraharmonic filter
        """

        contraharmonic_filtered_image = []

        for y in range(
            height
        ):  # get the neighbouring pixels of all the noised image pixels
            for x in range(width):
                neighbors = self.get_neighbors(
                    coordinates=(x, y), noised_image=noise_degraded_img
                )

                numerator = 0
                denominator = 0
                for element in neighbors:
                    if (
                        element == 0
                    ):  # ignores elements with '0' value to avoid division by zero
                        continue
                    numerator = numerator + element ** (q + 1)
                    denominator = denominator + element**q

                if denominator == 0:
                    contraharmonic_filtered_image.append(0)
                else:
                    contraharmonic_filtered_image.append(numerator / denominator)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(contraharmonic_filtered_image)

        return disp_img

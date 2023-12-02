from PIL import Image, ImageDraw
import random
import numpy as np


class ImageProcessor:
    def get_displayable_image(
        image_data: list[tuple[int, int, int]], width: int, height: int
    ) -> Image:
        """get displayable image

        Args:
            image_data (list[tuple[int, int, int]]): image data
            width (int): image width
            height (int): image height

        Returns:
            Image: displayable image
        """
        img = Image.new("RGB", (width, height))
        img.putdata(image_data)

        return img

    def get_displayable_palette(
        palette_data: list[tuple[int, int, int]], pixel_length: int
    ) -> Image:
        """get displayable palette

        Args:
            palette_data (list[tuple[int, int, int]]): palette data
            pixel_length (int): pixel size for each color in palette

        Returns:
            Image: displayable palette
        """
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

    def show_color_channel_images(
        image_data: list[tuple[int, int, int]], width: int, height: int, color: str
    ) -> Image:
        """Returns a color channel of the pcx image as displayable image

        Args:
            image_data (list[tuple[int, int, int]]): image data
            width (int): image width
            height (int): image height
            color (str): color channel

        Returns:
            Image: image using one color channel
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

    def get_grayscale_image(
        image_data: list[tuple[int, int, int]], width: int, height: int
    ) -> Image:
        """Returns a grayscale transformed version of the pcx image as a displayable image
        & the data of the grayscale transformed image

        Args:
            image_data (list[tuple[int, int, int]]): image data
            width (int): image width
            height (int): image height

        Returns:
            Image: grayscale image
        """

        grayscale_image_data = list()

        for pixel in image_data:
            grayscale_image_data.append(int((pixel[0] + pixel[1] + pixel[2]) / 3))

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(grayscale_image_data)

        return disp_img

    def get_negative_image(
        grayscale_data: list[tuple[int, int, int]], width: int, height: int
    ) -> Image:
        """Returns a negative transformed version of the pcx image as a displayable image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height

        Returns:
            Image: negative image
        """

        negative_image_data = list()

        for pixel in grayscale_data:
            negative_image_data.append(255 - pixel)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(negative_image_data)

        return disp_img

    def get_black_and_white_image(
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        threshold: int,
    ) -> Image:
        """Returns a black and white transformed version of the pcx image as a displayable image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            threshold (int): black and white threshold

        Returns:
            Image: black and white image
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
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        gamma: float,
    ) -> Image:
        """Returns a gamma transformed version of the pcx image as a displayable image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            gamma (float): gamma value

        Returns:
            Image: gamma transformed image
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
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        coordinates: tuple,
        radius: int = 1,
        pad: int = 0,
    ) -> list:
        """Returns the neighboring pixels of a given pixel coordinate

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            coordinates (tuple): coordinates of the pixel as (x, y)
            radius (int, optional):  radius of the neighboring area to get. Defaults to 1.
            pad (int, optional): value for out of bounds pixels. Defaults to 0.

        Returns:
            list: the neighboring pixels as a list
        """

        neighbors = list()
        # traverse each pixel starting from the upper-left to the lower-right pixels
        for y in range(coordinates[1] - radius, coordinates[1] + radius + 1):
            for x in range(coordinates[0] - radius, coordinates[0] + radius + 1):
                if (
                    x < 0 or x >= width or y < 0 or y >= height
                ):  # if out of bounds index
                    neighbors.append(pad)
                else:
                    neighbors.append(grayscale_data[y * width + x])

        return neighbors

    # Image functions
    def get_average_filtered_image(
        self,
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        radius: int = 1,
    ) -> Image:
        """Function to get the average-filtered (blur) image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            radius (int, optional): filter radius. Defaults to 1.

        Returns:
            Image: average filtered image
        """
        # stores the calculated values of the average-filtered image
        filtered_image = list()

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors(
                    grayscale_data, width, height, (x, y), radius
                )
                filtered_image.append(int(sum(neighbors) / len(neighbors)))

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_median_filtered_image(
        self,
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        radius: int = 1,
    ) -> Image:
        """Creates an median-filtered version of a grayscale version of an image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            radius (int, optional): mask radius. Defaults to 1.

        Returns:
            Image: median filtered image
        """

        filtered_image = []

        middle_index = int(((2 * radius + 1) ** 2) / 2)
        # 2*radius+1 is side of mask, square and you get the area or total number of pixels in mask
        # divide by 2, and getting the floor, you get the middle index (no need +1 since index starts from 0)
        # (optimization) this is calculated once here instead of everytime in the for loop below

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors(
                    grayscale_data, width, height, (x, y), radius
                )
                neighbors.sort()
                filtered_image.append(
                    neighbors[middle_index]
                )  # median is middle index of sorted list

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_highpass_filtered_image(
        self,
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        filter: int = 1,
    ) -> Image:
        """Returns a laplacian transformed version of the image

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            filter (int, optional): laplacian filter to use. Defaults to 1.

        Returns:
            Image: highpass filtered image
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
                neighbors = self.get_neighbors(
                    grayscale_data, width, height, (x, y)
                )  # using default 3x3 mask
                filtered_image.append(
                    sum(
                        [neighbors[i] * filter_used[i] for i in range(len(filter_used))]
                    )
                )

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(filtered_image)

        return disp_img

    def get_unsharp_masked_image(
        self, grayscale_data: list[tuple[int, int, int]], width: int, height: int
    ) -> Image:
        """Unsharps (sharpens) an image using the formula
        Unsharped_image = Grayscale_image + k * (Grayscale_image - average_filtered_image())

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height

        Returns:
            Image: unsharped image
        """

        blurred_image = list(
            self.get_average_filtered_image(grayscale_data, width, height).getdata()
        )
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
        self,
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        A: float = 1,
    ) -> Image:
        """returns a highboost filtered version of the image using the formula:
        highboosted_image = (A-1)Original + Highpass(1) where A is the intensity

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            A (float, optional): highboost filter intensity. Defaults to 1.

        Returns:
            Image: highboost filtered image
        """

        highpassed_image = list(
            self.get_highpass_filtered_image(grayscale_data, width, height, 2).getdata()
        )  # store the highpassed version of the image using the second filter
        original_image = grayscale_data  # apply the function for each
        highboosted_image = [
            (A - 1) * original_image[i] + highpassed_image[i]
            for i in range(len(original_image))
        ]

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(highboosted_image)

        return disp_img

    def get_image_gradient(
        self,
        grayscale_data: list[tuple[int, int, int]],
        width: int,
        height: int,
        mode: int = 1,
    ) -> Image:
        """Returns an image processed with Sobel operator

        Args:
            grayscale_data (list[tuple[int, int, int]]): grayscale data
            width (int): image width
            height (int): image height
            mode (int, optional): gradient direction. Defaults to 1.

        Returns:
            Image: image gradient
        """

        sobel_operator_x = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
        sobel_operator_y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]

        x_gradient = []  # stores the calculated values of the x gradient
        y_gradient = []  # stores the calculated values of the y gradient

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors(
                    grayscale_data, width, height, (x, y)
                )  # using default 3x3 mask
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

    def apply_salt_pepper(
        grayscale_data: list[int], width: int, height: int, probability: float
    ) -> Image:
        """Apply salt and pepper noise to the image

        Args:
            grayscale_data (list[int]): grayscale image data
            width (int): width of the image
            height (int): height of the image
            probability (float): probability for the noise

        Returns:
            Image: noised image
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

    def apply_gaussian(grayscale_data: list[int], width: int, height: int) -> Image:
        """Apply gaussian noise to the image

        Args:
            grayscale_data (list[int]): grayscale image data
            width (int): width of the image
            height (int): height of the image

        Returns:
            Image: noised image
        """

        mean = 35  # responsible for the bell curved shape of the distribution
        var = 10  # controls the amount of noise | variance determines the spread of the noise values | ^ Variance = Noisier Image

        gaussian_values = []

        # creating and storing the noise applied values
        for pixel in grayscale_data:
            noise = np.random.normal(mean, var, size=None)
            gaussian_values.append(pixel + noise)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(gaussian_values)

        return disp_img

    def apply_erlang(grayscale_data: list[int], width: int, height: int) -> Image:
        """Apply erlang noise to the image

        Args:
            grayscale_data (list[int]): grayscale image data
            width (int): width of the image
            height (int): height of the image

        Returns:
            Image: noised image
        """

        alpha = 2  # controls the shape of the noise distribution | amount of noise
        beta = 10  # Adjust the beta value to control the scale of the noise distribution (overall brightness of the image)

        erlang_values = []

        # creating and storing the noise applied values
        for pixel in grayscale_data:
            # noise =  np.random.normal(alpha, beta, size=None)
            noise = np.random.gamma(alpha, beta)
            erlang_values.append(pixel + noise)

        disp_img = Image.new("L", (width, height))
        disp_img.putdata(erlang_values)

        return disp_img

    def add_geometric_filter(
        self, width: int, height: int, noise_degraded_img: list[int]
    ) -> Image:
        """performs geometric filter restoration technique to the noised image

        Args:
            width (int): width of the image
            height (int): height of the image
            noise_degraded_img (list[int]): noised image

        Returns:
            Image: restored image
        """

        geometric_filtered_image = []

        for y in range(height):
            for x in range(width):
                neighbors = self.get_neighbors(
                    noise_degraded_img, width, height, (x, y)
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

    def add_contraharmonic(
        self, width: int, height: int, noise_degraded_img: list[int], q: int = 1
    ) -> Image:
        """performs geometric filter restoration technique to the noised image

        Args:
            width (int): width of the image
            height (int): height of the image
            noise_degraded_img (list[int]): noised image
            q (int): order of the filter

        Returns:
            Image: restored image
        """

        contraharmonic_filtered_image = []

        for y in range(
            height
        ):  # get the neighbouring pixels of all the noised image pixels
            for x in range(width):
                neighbors = self.get_neighbors(
                    noise_degraded_img, width, height, (x, y)
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

    def get_uncompressed_image_size(
        image_data: list[tuple[int, int, int]]
    ) -> dict[str, float]:
        """get the uncompressed image size

        Args:
            image_data (list[tuple[int, int, int]]): image data

        Returns:
            dict[str, float]: size info
        """
        palette = []
        for data in image_data:
            if data not in palette:
                palette.append(data)

        palette_color_bits = len(bin(len(palette) - 1)) - 2

        return {
            "image size": len(image_data) * palette_color_bits / 8,
            "palette size": len(palette) * 3,  # 3 byte color
        }

    def run_length_encoding(
        image_data: list[tuple[int, int, int]]
    ) -> tuple[list[int], list[tuple[int, int, int]], dict[str, float]]:
        """apply the run length encoding to the image data

        Args:
            image_data (list[tuple[int, int, int]]): image data

        Returns:
            tuple[list[int], list[tuple[int, int, int]], dict[str, float]]: rle data
        """
        palette = []
        rle_encoded_data = list()
        last_color = -1
        count = 0
        highest_count = 1

        # do the run length encoding
        for data in image_data:
            if data not in palette:
                palette.append(data)

            if data == last_color:
                count += 1
                if count > highest_count:
                    highest_count = count
            else:
                if last_color != -1:
                    rle_encoded_data.append(count)
                    rle_encoded_data.append(palette.index(last_color))
                last_color = data
                count = 1
        rle_encoded_data.append(count)
        rle_encoded_data.append(palette.index(last_color))

        highest_count_bits = len(bin(highest_count)) - 2
        # palette_color_bits = len(bin(len(palette) - 1)) - 2

        size_info = {
            "image size": highest_count_bits * len(rle_encoded_data) / 8,
            "palette size": len(palette) * 3,  # 3 byte color
        }

        return rle_encoded_data, palette, size_info

    def run_length_decode(
        rle_data: list[int],
        palette: list[tuple[int, int, int]],
        width: int,
        height: int,
    ) -> Image:
        """decode rle encoded data

        Args:
            rle_data (list[int]): rle encoded data
            palette (list[tuple[int, int, int]]): image palette
            width (int): width of the image
            height (int): height of the image

        Returns:
            Image: decoded image
        """
        image_data = list()
        for i in range(0, len(rle_data), 2):
            for j in range(rle_data[i]):
                image_data.append(palette[rle_data[i + 1]])

        disp_img = Image.new("RGB", (width, height))
        disp_img.putdata(image_data)

        return disp_img

    def huffman_coding(
        image_data: list[tuple[int, int, int]]
    ) -> tuple[str, dict[tuple[int, int, int], str], dict[str, float]]:
        """do the huffman coding for the image data

        Args:
            image_data (list[tuple[int, int, int]]): image data

        Returns:
            tuple[str, dict[tuple[int, int, int], str], dict[str, float]]: huffman coded data info
        """

        class Node:
            def __init__(self, value, key=None, left=None, right=None) -> None:
                self.value = value
                self.key = key
                self.left = left
                self.right = right

        # create frequency table
        freq_table = dict()
        for data in image_data:
            if data in freq_table:
                freq_table[data] += 1
            else:
                freq_table[data] = 1
        freq_table = dict(sorted(freq_table.items(), key=lambda item: item[1]))

        # create the huffman codes
        heap = [Node(freq_table[key], key) for key in freq_table]
        # create the tree
        while len(heap) > 1:
            left = heap.pop(0)
            right = heap.pop(0)
            entry = Node(left.value + right.value, left=left, right=right)
            for i in range(len(heap)):
                if heap[i].value > entry.value:
                    heap.insert(i, entry)
                    break
                if i == len(heap) - 1:
                    heap.append(entry)
            if len(heap) == 0:
                heap = [entry]
                break

        # map the codes
        huffman_codes = dict()
        # special case when there is only one color to code
        if not heap[0].left and not heap[0].right:
            huffman_codes[heap[0].key] = "0"
        # populate huffman codes dict
        heap[0].key = ""
        while len(heap) > 0:
            node = heap.pop()
            left = node.left
            right = node.right
            if left:
                if left.key:
                    huffman_codes[left.key] = "".join([node.key, "0"])
                else:
                    left.key = "".join([node.key, "0"])
                    heap.append(left)
            if right:
                if right.key:
                    huffman_codes[right.key] = "".join([node.key, "1"])
                else:
                    right.key = "".join([node.key, "1"])
                    heap.append(right)

        # convert the image pixels to huffman codes
        huffman_coded_image_data = ""
        for pixel in image_data:
            huffman_coded_image_data += huffman_codes[pixel]

        huffman_codes_size = 0
        for key in huffman_codes:
            huffman_codes_size += len(huffman_codes[key])

        size_info = {
            "image size": len(huffman_coded_image_data) / 8,
            "huffman codes size": huffman_codes_size / 8
            + len(huffman_codes) * 3,  # 3 byte color
        }

        return huffman_coded_image_data, huffman_codes, size_info

    def huffman_decode(
        huffman_data: str,
        huffman_codes: dict[tuple[int, int, int], str],
        width: int,
        height: int,
    ) -> Image:
        """decode the huffman encoded image data

        Args:
            huffman_data (str): huffman encoded data
            huffman_codes (dict[tuple[int, int, int], str]): huffman codes
            width (int): image width
            height (int): image height

        Returns:
            Image: decoded image
        """
        huffman_codes = {v: k for k, v in huffman_codes.items()}
        image_data = list()

        current_string = ""
        for bit in huffman_data:
            current_string += bit
            if current_string in huffman_codes:
                image_data.append(huffman_codes[current_string])
                current_string = ""

        disp_img = Image.new("RGB", (width, height))
        disp_img.putdata(image_data)

        return disp_img

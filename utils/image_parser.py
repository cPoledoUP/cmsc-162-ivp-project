from PIL import Image


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

    def process_image_data(self) -> dict[str, int | list[tuple[int, int, int]] | str]:
        """Processes the pcx file

        Raises:
            Exception: pcx file cannot be parsed by the program

        Returns:
            dict[str, int | list[tuple[int, int, int]] | str]: image information
        """

        # https://people.sc.fsu.edu/~jburkardt/txt/pcx_format.txt
        # http://www.fysnet.net/pcxfile.htm

        dimensions = self.get_window()
        width = dimensions[2] - dimensions[0] + 1
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

        all_data = (
            f"File Name: {self.location}\n"
            f"Manufacturer: {self.get_manufacturer()}\n"
            f"Version: {self.get_version()}\n"
            f"Encoding: {self.get_encoding()}\n"
            f"Bits per Pixel: {self.get_bits_per_pixel()}\n"
            f"Image Dimensions: {self.get_window()}\n"
            f"HDPI: {self.get_hdpi()}\n"
            f"VDPI: {self.get_vdpi()}\n"
            f"Number of Color Planes: {self.get_n_planes()}\n"
            f"Bytes per Line: {self.get_bytes_per_line()}\n"
            f"Palette Information: {self.get_palette_info()}\n"
            f"Horizontal Screen Size: {self.get_h_screen_size()}\n"
            f"Vertical Screen Size: {self.get_v_screen_size()}"
        )

        return {
            "width": width,
            "height": height,
            "pixel_data": rgb_image_data,
            "palette_data": palette,
            "metadata": all_data,
        }


class ImageParser:
    def parse_image(
        location: str,
    ) -> dict[str, int | list[tuple[int, int, int] | int] | str]:
        """General image parser function

        Args:
            location (str): location of the image

        Returns:
            dict[str, int | list[tuple[int, int, int] | int] | str]: image information
        """
        if location.endswith("pcx"):
            return PcxImage(location).process_image_data()

        img = Image.open(location)
        width, height = img.size

        return {
            "width": width,
            "height": height,
            "pixel_data": list(img.getdata()),
            "palette_data": None,
            "metadata": f"File Name: {location.split("/")[-1]}\nDimensions: {width} x {height}",
        }

from dataclasses import dataclass
import numpy as np
from PIL import Image

# encoder/decoder for lossloss image file format: https://qoiformat.org/
# ./test_images also from https://qoiformat.org/

@dataclass
class Pixel:
    r: int
    g: int
    b: int
    a: int

    def __repr__(self) -> str:
        return f"Pixel: ({self.r}, {self.g}, {self.b}, {self.a})"

    def diff(self, decode_value):
        r = (self.r + (((decode_value >> 4) & 0b11) - 2)) % 256
        g = (self.g + (((decode_value >> 2) & 0b11) - 2)) % 256 
        b = (self.b + ((decode_value        & 0b11) - 2)) % 256
        return Pixel(r, g, b, self.a)
    
    def diff_luma(self, dg, byte):
        nr = byte >> 4
        nb = byte & 0b1111
        ng = dg - 32
        g = (self.g + ng         ) % 256
        r = (self.r + ng - 8 + nr) % 256
        b = (self.b + ng - 8 + nb) % 256
        return Pixel(r, g, b, self.a)

    def hash(self):
        return ((self.r * 3 + self.g * 5 + self.b * 7 + self.a * 11) % 64)

@dataclass
class Qoi:
    file: str
    header: dict
    image: list

    QOI_OP_RGB  = 0b11111110 # 254
    QOI_OP_RGBA = 0b11111111 # 255

    QOI_OP_INDEX = 0b00 # 0
    QOI_OP_DIFF  = 0b01 # 1
    QOI_OP_LUMA  = 0b10 # 2
    QOI_OP_RUN   = 0b11 # 3

    def __init__(self, file_name):
        self.header = { "name": file_name }
        
    def load(self):
        self.file = open(self.header['name'], "rb")
        header = bytearray(self.file.read(14))
        if header[0:4] != b'qoif': return None
        self.header["head"      ] = b'qoif'
        self.header["width"     ] = header[4] * 16**6 + header[5] * 16**4 + header[6]  * 16**2 + header[7]
        self.header["height"    ] = header[8] * 16**6 + header[9] * 16**4 + header[10] * 16**2 + header[11]
        self.header["channels"  ] = header[12]
        self.header["colorspace"] = header[13]
        self.image = []
        self.__decode()
        return self

    def __repr__(self) -> str:
        return str(self.header)
    
    def height(self) -> int:
        return self.header['height']

    def width(self) -> int:
        return self.header['width']

    def channels(self) -> int:
        return self.header['channels']

    def image(self):
        return self.image

    def image_data(self):
        if self.channels() == 3:
            data = [np.array([np.uint8(x.r), np.uint8(x.g), np.uint8(x.b)]) for x in self.image]
        elif self.channels() == 4:
            data = [np.array([np.uint8(x.r), np.uint8(x.g), np.uint8(x.b), np.uint8(x.a)]) for x in self.image]
        array = np.array(data).reshape(self.height(), self.width(), self.channels())
        return array

    def __read_byte(self):
        byte = self.file.read(1)
        if byte == b'':
            return None
        else:
            return int.from_bytes(byte, 'little')
       
    def __read_bytes(self, count):
        read = []
        for i in range(count):
            byte = self.file.read(1)
            if byte == b'':
                return None
            read.append(byte)
            
        return [int.from_bytes(x, 'little') for x in read]

    def __decode(self):
        image_size = self.width() * self.height() * self.channels()
        decoded_image = []
        
        array = [Pixel(0, 0, 0, 0) for _ in range(64)]
        pixel = Pixel(0, 0, 0, 255) # start value of pixel

        for i in range(image_size):
            value = self.__read_byte()
            if value is None: break

            if value == self.QOI_OP_RGB:
                r, g, b = self.__read_bytes(3)
                pixel = Pixel(r, g, b, pixel.a)
                array[pixel.hash()] = pixel
                decoded_image.append(pixel)
            elif value == self.QOI_OP_RGBA:
                r, g, b, a = self.__read_bytes(4)
                pixel = Pixel(r, g, b, a)
                array[pixel.hash()] = pixel
                decoded_image.append(pixel)
            else:
                decode_type = value // 64
                decode_value = value % 64
                if decode_type == self.QOI_OP_INDEX:
                    pixel = array[decode_value]
                    decoded_image.append(pixel)
                elif decode_type == self.QOI_OP_DIFF:
                    pixel = pixel.diff(decode_value)
                    array[pixel.hash()] = pixel
                    decoded_image.append(pixel)
                elif decode_type == self.QOI_OP_LUMA:
                    next_byte = self.__read_byte()
                    pixel = pixel.diff_luma(decode_value, next_byte)
                    array[pixel.hash()] = pixel
                    decoded_image.append(pixel)
                elif decode_type == self.QOI_OP_RUN:
                    [decoded_image.append(pixel) for _ in range(decode_value + 1)]

        self.image = decoded_image[0:-8] # discard 8 end marker


image = Qoi("./test_images/testcard.qoi").load()
i=Image.fromarray(image.image_data())
i.save("test_image.png")

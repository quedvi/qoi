import numpy as np
from PIL import Image

# encoder/decoder for lossloss image file format: https://qoiformat.org/
# ./test_images also from https://qoiformat.org/

class Pixel:
    def __init__(self, r, g, b, a) -> 'Pixel':
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self) -> str:
        return f"Pixel: ({self.r}, {self.g}, {self.b}, {self.a})"

    def decode_diff(self, decode_value) -> 'Pixel':
        r = (self.r + (((decode_value >> 4) & 0b11) - 2)) % 256
        g = (self.g + (((decode_value >> 2) & 0b11) - 2)) % 256 
        b = (self.b + (( decode_value       & 0b11) - 2)) % 256
        return Pixel(r, g, b, self.a)
    
    def decode_diff_luma(self, dg, byte) -> 'Pixel':
        nr = byte >> 4
        nb = byte & 0b1111
        ng = dg - 32
        g = (self.g + ng         ) % 256
        r = (self.r + ng - 8 + nr) % 256
        b = (self.b + ng - 8 + nb) % 256
        return Pixel(r, g, b, self.a)

    def hash(self) -> int:
        return ((self.r * 3 + self.g * 5 + self.b * 7 + self.a * 11) % 64)

class Qoi:
    QOI_OP_RGB  = 0b11111110 # 254
    QOI_OP_RGBA = 0b11111111 # 255

    QOI_OP_INDEX = 0b00 # 0
    QOI_OP_DIFF  = 0b01 # 1
    QOI_OP_LUMA  = 0b10 # 2
    QOI_OP_RUN   = 0b11 # 3

    def load(self, file_name) -> 'Qoi':
        self.header = { "name": file_name }
        self.file = open(file_name, "rb")

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

    def save(self, file_name, data) -> 'Qoi':
        height, width, channels = data.shape
        self.image = data
        self.file = open(file_name, "wb")
        self.header = { "name": file_name }
        self.header["head"      ] = b'qoif'
        self.header["width"     ] = width
        self.header["height"    ] = height
        self.header["channels"  ] = channels
        self.header["colorspace"] = 0


        self.__write_header()
        self.__encode()
        self.file.close()
        return self

    def __encode(self) -> None:
        channels = self.header["channels"]
        print(channels)
        for i in range(self.height()):
            for j in range(self.width()):
                if channels == 3:
                   frame = bytearray(4)
                   frame[0] = self.QOI_OP_RGB
                   frame[1] = self.image[i,j,0]
                   frame[2] = self.image[i,j,1]
                   frame[3] = self.image[i,j,2]
                   self.file.write(frame)
                   continue

                if channels == 4:
                   frame = bytearray(5)
                   frame[0] = self.QOI_OP_RGBA
                   frame[1] = self.image[i,j,0]
                   frame[2] = self.image[i,j,1]
                   frame[3] = self.image[i,j,2]
                   frame[4] = self.image[i,j,3]
                   self.file.write(frame)
                   continue
        self.file.write(bytearray(8))

    def __repr__(self) -> str:
        return str(self.header)
    
    def height(self) -> int:
        return self.header["height"]

    def width(self) -> int:
        return self.header["width"]

    def channels(self) -> int:
        return self.header["channels"]

    def image(self) -> list:
        return self.image

    def image_data(self) -> np.array:
        if self.channels() == 3:
            data = [np.array([np.uint8(x.r), np.uint8(x.g), np.uint8(x.b)]) for x in self.image]
        elif self.channels() == 4:
            data = [np.array([np.uint8(x.r), np.uint8(x.g), np.uint8(x.b), np.uint8(x.a)]) for x in self.image]
        array = np.array(data).reshape(self.height(), self.width(), self.channels())
        return array

    def __write_header(self) -> None:
        self.file.write(bytearray(self.header["head"]))
        self.file.write(self.__convert_int(self.header["width" ]))
        self.file.write(self.__convert_int(self.header["height"]))
        self.file.write(self.header["channels"  ].to_bytes(1, byteorder = 'little'))
        self.file.write(self.header["colorspace"].to_bytes(1, byteorder = 'little'))

    def __convert_int(self, number) -> bytearray:
        bytes = bytearray(4)
        for i in range(4):
            bytes[3-i] = number % 256
            number = number >> 8
        return bytes

    def __read_byte(self) -> int:
        byte = self.file.read(1)
        if byte == b'':
            return None
        else:
            return int.from_bytes(byte, 'little')
       
    def __read_bytes(self, count) -> list:
        return [ self.__read_byte() for _ in range(count)]

    def __decode(self) -> None:
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
                    pixel = pixel.decode_diff(decode_value)
                    array[pixel.hash()] = pixel
                    decoded_image.append(pixel)
                elif decode_type == self.QOI_OP_LUMA:
                    next_byte = self.__read_byte()
                    pixel = pixel.decode_diff_luma(decode_value, next_byte)
                    array[pixel.hash()] = pixel
                    decoded_image.append(pixel)
                elif decode_type == self.QOI_OP_RUN:
                    [decoded_image.append(pixel) for _ in range(decode_value + 1)]

        self.image = decoded_image[0:-8] # discard 8 end marker

# image = Qoi().load("./test_images/qoi_logo.qoi")
# print(image)
# new_image = Qoi().save("test.qoi", image.image_data())
# data = image.image_data()

# Qoi().save('test.qoi', data)

image = Qoi().load("test.qoi")
print(image)
i=Image.fromarray(image.image_data())
i.save("test.png")

# load_image = open("test.qoi", "rb")
# read = bytearray(load_image.read(14))
# print(read)

# i=Image.fromarray(image.image_data())
# i.save("test_image.png")

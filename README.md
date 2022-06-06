# Python QOI
[QOI (Quite OK Image format)](https://github.com/phoboslab/qoi) is a new lossless image format that achieves compression rates close to PNG with a 20x-50x faster encoding.

This here is a naive Python way of implementing the QOI compression format and of course much slower than the C implementation. 

There's a [python wrapper](https://github.com/kodonnell/qoi) around the original C implementation, which retains the C performance.

The CLI interface was liberally borrowed from [Python QOI (py-qoi)](https://github.com/mathpn/py-qoi). The encoder/decoder is an reimplementation. 

## Requirements

The only requirement besides Python 3.10+ is Pillow to load and save images in formats other than QOI, and numpy for matrix manipulations.

## Usage

To encode an image:

    python3 qoi-quedvi/qoi.py -e -f image_file.png

The input image may be of any [pillow-supported format](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).
A file with name image_file.qoi will be saved on the same folder as the original image.

To decode a QOI image:

    python3 qoi-conv/qoi.py -d -f image_file.qoi

A file with name image_file.png will be saved on the same folder as the original image.


    usage: qoi-quedvi/qoi.py [-h] [-e] [-d] [-f FILE_PATH]
    optional arguments:
      -h, --help            show this help message and exit
      -e, --encode
      -d, --decode
      -v, --verbose         get additional info
      -f FILE_PATH, --file-path FILE_PATH
                            path to image file to be encoded or decoded
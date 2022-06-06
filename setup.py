from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='qoi-conv',
    version='1.0.1',    
    description='A simple implementation of the QOI image format in Pyhton.',
    long_description=long_description,
    long_description_content_type="text/markdown",    
    url='https://github.com/quedvi/qoi',
    author='Martin Oehzelt',
    author_email='oehzelt@gmx.at',
    license='MIT',
    packages=['qoi-conv'],
    install_requires=['pillow>=9.0.1',
                      'numpy>=1.22.3',
                      ],

    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)

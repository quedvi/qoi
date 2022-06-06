from setuptools import setup

setup(
    name='QOI',
    version='0.1.0',    
    description='A simple implementation of the QOI image format in Pyhton.',
    url='https://github.com/quedvi/qoi',
    author='Martin Oehzelt',
    author_email='oehzelt@gmx.at',
    license='MIT',
    packages=['qoi'],
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

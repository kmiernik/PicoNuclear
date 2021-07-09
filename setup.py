import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PicoNuclear',
    version='0.1.0',
    author='Krzysztof Miernik',
    author_email='kamiernik@gmail.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_dir={'PicoNuclear':'PicoNuclear'},
    #package_data={'': ['config/*.xml'],
                  #'': ['demo/*.txt'],
                #},
    scripts=['bin/mini_pet.py',
             'bin/miniPET.py',
             'bin/pico_capture.py'],
    license='LICENSE.txt',
    description='Front-end for picoscope to be used for nuclear physics\
            related projects setup',
    long_description=long_description,
    url=['https://github.com/kmiernik/PicoNuclear'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=['matplotlib', 'numpy', 'scipy', 'picosdk']
)

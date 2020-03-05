from distutils.core import setup

setup(
    name='PicoNuclear',
    version='0.1.0',
    author='Krzysztof Miernik',
    author_email='kamiernik@gmail.com',
    packages=['PicoNuclear'],
    package_dir={'PicoNuclear': ''},
    package_data={'PicoNuclear': ['config/*.xml']},
    url=['https://github.com/kmiernik/PicoNuclear'],
    scripts=['bin/mini_pet.py',
             'bin/pico_capture.py'],
    license='LICENSE.txt',
    description='Front-end for picoscope to be used for nuclear physics\
            related projects setup',
    long_description=open('README.txt').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=['matplotlib', 'numpy', 'scipy', 'picosdk']
)

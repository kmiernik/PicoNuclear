from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='PicoNuclear',
    version='0.2.0', 
    description='Front-end for picoscope to be used for nuclear physics related projects',
    long_description=long_description,  
    long_description_content_type='text/markdown',
    url='https://github.com/kmiernik/PicoNuclear', 
    author='K. Miernik',
    author_email='kamiernik@gmail.com',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Linux',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    keywords='sample, setuptools, development', 
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'), 
    python_requires='>=3.6, <4',
    #install_requires=['numpy', 'picosdk'],  # Optional
    package_data={  
        'PicoNuclear': ['data/*.*'],
    },
    scripts=['src/bin/miniPET.py', 'src/bin/pico_capture.py'],
    project_urls={  
        'Bug Reports': 'https://github.com/kmiernik/PicoNuclear/issues'
    }
)

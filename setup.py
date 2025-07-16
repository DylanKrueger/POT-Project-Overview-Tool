from setuptools import setup, find_packages

setup(
    name="project-overview",
    version="0.0.2",
    description="Directory tree with LOC stats",
    author="DylanKrueger",
    packages=find_packages(),
    install_requires=[
        "colorama",
        "pyperclip",
        "setuptools",
        "psutil",
        "tqdm",    
    ],
    entry_points={
        'console_scripts': [
            'pot=pot.cli:main', 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
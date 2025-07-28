from setuptools import setup, find_packages
import os

setup(
    name="project-overview",
    version="0.0.3",
    description="Directory tree with LOC stats, JSON support, and web view",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="DylanKrueger",
    packages=find_packages(),
    package_data={
    'VLTRE': ['stages/*'],  # include all files in stages directory
    },
    include_package_data=True,
    install_requires=[
        "colorama",
        "pyperclip",
        "setuptools",
        "psutil",    # for system info if needed
        "tqdm",     # for progress bars if used
        "matplotlib",
    ],
    extras_require={
        'clipboard': ['pyperclip'],
        'dev': [
            # Add dev dependencies here
        ],
    },
    entry_points={
        'console_scripts': [
            'POT=VLTRE.cli:main',  # Ensure your cli.py has a main() function
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires='>=3.8',  # Specify minimum Python version
)
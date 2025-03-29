from setuptools import setup, find_packages

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reddit-flair-analyzer",
    version="1.0.1",
    author="Manoj Desai",
    author_email="themanojdesai@gmail.com",  # Use your actual email
    description="A professional tool for analyzing which Reddit post flairs have the highest chance of going viral",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/themanojdesai/reddit-flair-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/themanojdesai/reddit-flair-analyzer/issues",
        "Documentation": "https://github.com/themanojdesai/reddit-flair-analyzer/tree/main/docs",
        "Source Code": "https://github.com/themanojdesai/reddit-flair-analyzer",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Operating System :: OS Independent",
    ],
    keywords="reddit, data analysis, visualization, flair, social media, analytics, viral, marketing",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "praw>=7.0.0",
        "pandas>=1.0.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "numpy>=1.19.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "openpyxl>=3.0.0",
        "tqdm>=4.50.0",
        "colorlog>=6.0.0",
        "tabulate>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "reddit-analyze=redditflairanalyzer.cli:main",
        ],
    },
    include_package_data=True,
)
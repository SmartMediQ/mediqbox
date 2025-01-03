from setuptools import setup, find_packages

with open("README.md", "r") as fp:
  long_description = fp.read()

setup(
  name="mediqbox",
  version="0.1.0",
  author="Smartmediq",
  author_email="dev@smartmediq.com",
  description="A toolbox for smart medical information processing and application development.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/SmartMediQ/mediqbox",
  packages=find_packages(
    exclude=["tests", "tests.*"],
  ),
  classifiers=[
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
  python_requires=">=3.9",
  install_requires=[
    "aiofiles",
    "aiohttp",
    "biopython",
    "pydantic[email]",
  ],
)

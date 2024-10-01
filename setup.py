from setuptools import setup, find_packages

setup(
    name="sensibull_quotes",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.1",
    ],
    author="Prashant Kumar",
    author_email="its@undef.in",
    description="A Python package to fetch and process live derivative prices and quotes from Sensibull's API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/itsundef/sensibull_quotes",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

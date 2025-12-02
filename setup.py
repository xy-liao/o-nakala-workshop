from setuptools import setup, find_packages

setup(
    name="nakala",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "jupyter>=1.0.0",
        "ipywidgets>=8.0.0",
        "pandas>=2.0.0",
    ],
    author="LIAO Shueh-Ying",
    description="NAKALA API Python Package for Workshop",
)
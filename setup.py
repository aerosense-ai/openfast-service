from setuptools import setup


setup(
    name="openfast-service",
    version="0.1.0",
    py_modules=["app"],
    install_requires=[
        "octue==0.17.0",
    ],
)

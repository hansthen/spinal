from setuptools import setup

with open("requirements.txt", "r") as requirements:
    install_requires = requirements.read().splitlines()

setup(
    name="spinal",
    version="0.1",
    py_modules=["spinal"],
    entry_points={"console_scripts": ["spinal=spinal:main"]},
    install_requires=install_requires,
    license="Creative Commons Attribution-Noncommercial-Share Alike license",
    long_description=open("README.md").read(),
)

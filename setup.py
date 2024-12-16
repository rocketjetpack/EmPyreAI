"""A module for the Empire AI Alpha system to abstract Base Command and Slurm operations so
they may be completed without elevated privileges."""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="EmPyreAI",
    version="1.0.0",
    description="A Python module for the Empire AI project.",
    long_description=long_description,
    url="https://github.com/rocketjetpack/EmPyreAI",
    author="Kali McLennan",
    author_email="help@empire-ai.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programmiong Language :: Python :: 3",
        ],
    keywords="cmsh, basecommand, empireai",
    package_dir={"": ""}
    python_requires=">3.7, <4",
    install_rquires=["json", "argparse", "os", "sys", "prettytable"]
    )

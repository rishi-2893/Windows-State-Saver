from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="state_saver",
    version="0.0.10",
    description="Saves the current state of a Windows laptop and then reopen it.",
    # package_dir={"": "app"},
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishi-2893/Windows-State-Saver",
    author="Rishi Patel",
    author_email="rptl2803@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points = {
        "console_scripts": [
        "state = app.Main:run",
        ]
    },
    install_requires=["importlib_resources"],
    include_package_data=True
)
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="verilog_timings_parser",
    version="0.0.1",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Antmicro Ltd.",
    author_email="contact@antmicro.com",
    entry_points={
        'console_scripts': ['verilog-timings-to-liberty=verilog_timings_parser.convert_verilog_timings_to_liberty:main']  # noqa: E501
    },
    install_requires=[
        'quicklogic_timings_importer @ git+https://github.com/antmicro/quicklogic-timings-importer#egg=quicklogic_timings_importer',  # noqa: E501
        'ply',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

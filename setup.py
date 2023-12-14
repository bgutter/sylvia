from distutils.core import setup

setup(
    name="sylvia",
    packages=["sylvia"],
    version="0.3",
    description="A tool for searching pronunciations in the CMU Pronouncing Dictionary with a regular-expression-like syntax.",
    author="Brandon Guttersohn",
    author_email="bguttersohn@gmail.com",
    url="https://github.com/bgutter/sylvia",
    download_url="https://github.com/bgutter/sylvia/archive/development/0.3.tar.gz",
    keywords=["cmudict", "phoneme", "phonetic", "rhyme", "regex"],
    classifiers=[],
    package_data={"sylvia": ["data/cmudict.sylviabin"]},
    install_requires=[
        "epc",
    ],
)

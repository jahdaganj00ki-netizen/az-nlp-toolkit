from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="az-nlp-toolkit",
    version="0.3.0",
    author="Shahin Hasanov",
    author_email="shahin.hasanov@example.com",
    description="NLP toolkit for Azerbaijani language processing: tokenization, stemming, transliteration, NER for trade documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShahinHasanov90/az-nlp-toolkit",
    project_urls={
        "Bug Tracker": "https://github.com/ShahinHasanov90/az-nlp-toolkit/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Azerbaijani",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "az_nlp": ["../data/*.txt", "../data/*.json"],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "nltk>=3.8",
        "regex>=2023.0",
        "unicodedata2>=15.0.0",
        "sentence-transformers>=2.2.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1.0",
        ],
    },
)

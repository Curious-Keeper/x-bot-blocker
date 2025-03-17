from setuptools import setup, find_packages

setup(
    name="x_bot_blocker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tweepy",
        "pandas",
        "numpy",
        "scikit-learn",
        "python-dotenv",
        "pyyaml",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-xdist",
        ],
    },
) 
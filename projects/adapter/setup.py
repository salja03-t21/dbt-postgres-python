from setuptools import setup, find_packages

setup(
    name="dbt-postgres-python",
    version="1.7.18",
    description="Run python scripts from any dbt project. This project is based on the project https://github.com/fal-ai/fal initially authored by FAL.AI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kudryk/dbt-postgres-python",
    author="Features & Labels, Mark Kudryk",
    author_email="hello@fal.ai, kudryk@me.com",
    packages=find_packages("src"),  # Adjusting to match the 'src' directory
    package_dir={"": "src"},  # Specifies that packages are found in the 'src' directory
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",  # Specify the license if you have one
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dbt-core>=1.7,<=1.9",
        "pandas>=1.5.3",
        "numpy<2",
        "virtualenv>=20.21.1",
        "sqlalchemy>=1.4.52",
        "packaging>=23",
        "fal>=0.10.0",
        "importlib-metadata>=6.11.0"
    ],
    extras_require={
        "postgres": [],
        "teleport": ["s3fs>=2022.8.2"],
    },
    keywords=["dbt", "pandas", "fal", "runtime"],
    include_package_data=True,  # Include additional files specified in MANIFEST.in
)

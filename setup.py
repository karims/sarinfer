from setuptools import setup, find_packages

setup(
    name='sarinfer',
    version='0.1.0',
    description='Sarinfer: Fast, scalable inference engine for LLMs with TensorStore and GPU/CPU management',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://yourprojecturl.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'typer',          # CLI framework
        'click',          # Dependency for Typer
        'numpy',          # Core dependency for tensor operations
        'pytest',         # Testing
        'flake8',         # Linting
        'sphinx',         # Documentation generation
        'watchdog',       # For watching file changes (servedocs)
        'coverage',       # Test coverage
        'tox',            # For testing on multiple Python versions
        'tensorstore',    # TensorStore integration for efficient storage
        'uvicorn',        # ASGI server if API/REST endpoints are added later
        'fastapi',        # If FastAPI is used for APIs
        'boto3',
        'moto',
        'pymongo',
        'mongomock',
        'pytest-mock-resources[mongo]',
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'coverage',
            'tox',
            'watchdog',
        ],
    },
    entry_points={
        'console_scripts': [
            'sarinfer=sarinfer.cli:app',  # Connect the Typer CLI
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

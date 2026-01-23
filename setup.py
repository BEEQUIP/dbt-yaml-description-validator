from setuptools import setup, find_packages

setup(
    name="dbt-yaml-description-validator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ruamel.yaml>=0.17.0",
    ],
    entry_points={
        "console_scripts": [
            "dbt-yaml-description-validator=dbt_yaml_description_validator.runner:main",
        ]
    },
)

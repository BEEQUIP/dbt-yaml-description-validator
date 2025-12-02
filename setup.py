from setuptools import setup, find_packages

setup(
    name="dbt-yaml-description-validator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=5.1",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "check-description-ends-with-dot=dbt_yaml_description_validator.check_dot:main"
        ]
    },
)

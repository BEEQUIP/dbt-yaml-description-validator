# dbt yaml validator

A custom pre-commit repository where we manage what our descriptions should look like in a dbt project


The following code should be added to the pre-commit-config.yaml file of the repository. 

fail_fast: true
repos:
- repo: https://github.com/BEEQUIP/dbt-yaml-description-validator
  rev: main
  hooks:
    - id: check-description-starts-with-capital-fix
      files: '(?i)schema\.ya?ml$'

    - id: check-description-double-spaces-fix
      files: '(?i)schema\.ya?ml$'

    - id: check-description-ends-with-period-fix
      files: '(?i)schema\.ya?ml$'

    - id: check-description-no-symbols
      files: '(?i)schema\.ya?ml$'

    - id: check-description-starts-with-article
      files: '(?i)schema\.ya?ml$'
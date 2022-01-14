# Package {{ cookiecutter._pkg_name }}


Please update this with a brief introduction of the package.


## Package development

The initial version of this package was created by the WorkFlow Package Manager CLI tool, please refer to
the [documentation](https://wfpm.readthedocs.io) for details on the development procedure including
versioning, updating, CI testing and releasing.


## Inputs

Please list all input parameters


## Outputs

Please list all outputs


## Usage

### Run the package directly

With inputs prepared, you should be able to run the package directly using the following command.
Please replace the params file with a real one (with all required parameters and input files). Example
params file(s) can be found in the `tests` folder.

```
nextflow run {{ cookiecutter._repo_account|lower }}/{{ cookiecutter._repo_name }}/{{ cookiecutter._pkg_name }}/main.nf -r {{ cookiecutter._pkg_name }}.v{{ cookiecutter.pkg_version }} -params-file <your-params-json-file>
```

### Import the package as a dependency

To import this package into another package as a dependency, please follow these steps at the
importing package side:

1. add this package's URI `{{ cookiecutter._repo_server }}/{{ cookiecutter._repo_account|lower }}/{{ cookiecutter._repo_name }}/{{ cookiecutter._pkg_name }}@{{ cookiecutter.pkg_version }}` in the `dependencies` list of the `pkg.json` file
2. run `wfpm install` to install the dependency
3. add the `include` statement in the main Nextflow script to import the dependent package from this path: `./wfpr_modules/{{ cookiecutter._repo_server }}/{{ cookiecutter._repo_account|lower }}/{{ cookiecutter._repo_name }}/{{ cookiecutter._pkg_name }}@{{ cookiecutter.pkg_version }}/main.nf`

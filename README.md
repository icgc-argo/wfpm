# WorkFlow Package Manager

The WFPM CLI is a command line tool for workflow package authoring and management, it's developed in
Python and runs on a Linux or Mac OS environment. WFPM CLI provides assistance to write shareable/reusable
workflow packages. A package can be a single step tool (aka `process` in [Nextflow](https://www.nextflow.io/)),
a function or a workflow with multiple steps chained together.

We get a lot of inspiration from [NPM](https://docs.npmjs.com/about-npm) (node package manager), which
is one of the most successful package mangement systems. The bioinformatics workflow development
community would greatly appreciate something like NPM to facilitate and accelerate collaborative
development via reusable packages.

NOTE: WFPM CLI is in active development, more features, documentation and tutorials are coming.


## Best practices we follow in scientific workflow development

* **Reproducible** - same input, same code, same result
  - containerize all software tools (including scripts, binary executables) and specific OS environment
  - tag every image build and associate it with workflow source code release

* **Portable** - run on different platforms, by different users
  - containerize all software tools (containerization appeared again, it is a good friend :blush:)
  - use cross-platform workflow languages / orchestration systems, eg, Nextflow, WDL etc

* **Composable** - enable collaborative development
  - break down big tasks into small tasks (each carried out by a small software tool / component)
  - one tool / component per container image
  - version and release independently every tool and its associated container image

* **Findable** - easy to find by research community members
  - register components / workflows in public tool registries, such as Dockstore, BioContainers etc
  - release workflow source code via GitHub Releases

* **Testable** - deliver with high confidence
  - must have tests for every tool / component / workflow
  - configure / enable continuous integration testing


## WFPM prerequisites

Please ensure the following prerequisites are met before moving on to installation.

```
python >= 3.6
pip >= 20.0 (only required for installation)
bash >= 3.2
git >= 2.0
nextflow >= 20.10
docker >= 19.0
```


## Installation

Install WFPM CLI with a single command:

```
pip install wfpm
```

To update to the latest version, run `pip install --upgrade wfpm`


## Demo use case

To show usage information of WFPM CLI, just run `wfpm --help`.

The following instructions will walk you through the steps to create and public a demo tool package.

1. Prepare a GitHub repository under an organization account

Before you start, please make sure you create a repository (with name at your choice) under
a GitHub organization account. This is because GitHub Container Registry (ghcr.io) is not
available for personal account. We will be using ghcr.io registry to keep the container image
created and used by the demo tool package.

You also need to create a Personal Access Token (PAT) in order to access GitHub Container Registry,
go to: your account => settings => Personal access tokens => Generate new token. Please select
`write:packages` scope for the token.

Once PAT is created, please copy the token and add it to the repository you created above. Here are the
buttons to click through: Settings (under the repository page) => Secrets => New repository secret.
For name, please use `CR_PAT`, value is the PAT you just created.


2. Initialize a project directory for developing/managing workflow packages

```
wfpm init
```

Please follow the prompt to provide necessary information. Most important information
include `github_account` and `project_slug` (this is the project name, and will also be the
GitHub repo name, please make sure it matches what you have created at step 1.).
Once completed, you should see something similar as below:

```
Project initialized in ...
Git repo initialized and first commit done. When ready, you may push to github.com using:
git push -u origin main
```

When you are ready, as suggested above you can push the code to GitHub. Upon push received at
GitHub, CI/CD testing will be automatically triggered (if you enabled GitHub Actions for your account).


3. Create your first tool package

```
wfpm new tool fastqc
```

We use the bioinformatics tool `fastqc` as an example here for demonstration purposes. You
can pretty much use the default values in the prompt to advance forward. Upon completion,
you should see a message like `New package created in: fastqc`

As part of the best practices, code for a new tool or a new version should be added to a
particular branch named as `<tool_package_name>@<tool_package_version>`. To do so:

```
git checkout -b fastqc@0.1.0
```

Assume you used the default values for tool name (`fastqc`) and version (`0.1.0`). Now, you can
add the generated code to git, commit and push.

```
git add .
git commit -m 'added first tool: fastqc@0.1.0'
git push -u origin fastqc@0.1.0
```

Upon receiving the push, GitHub will automatically start CI/CD via GitHub Actions. If the test
passes, you can create a PR against the `main` branch.


4. Release your first tool package

For demo purpose, when you merge the above PR, in the comment field, you may type a special
command to instruct GitHub Actions to perform a release process. The special command
is `[release]`. With this GitHub will first merge the `fastqc@0.1.0` branch to the `main` branch,
then starts CI/CD process, once tests are successful, a release of your first tool package
will be made automatically.

Your released package can then be imported and used by anyone (of course including yourself) in their
workflows. How to do that? We will have another demo use case for it. Stay tuned!

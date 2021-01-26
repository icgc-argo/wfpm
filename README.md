# WorkFlow Package Manager

The WFPM CLI is a command line tool for workflow package authoring and management, it's developed in
Python and runs on a Linux or Mac OS environment. WFPM CLI provides assistance to write shareable/reusable
workflow packages. A package can include one or more of these items: a single step tool
(aka `process` in [Nextflow](https://www.nextflow.io/)), a function or a workflow with multiple steps
chained together.

We get a lot of inspiration from [NPM](https://docs.npmjs.com/about-npm) (node package manager), which
is one of the most successful package mangement systems. The bioinformatics workflow development
community would greatly appreciate something like NPM to facilitate and accelerate collaborative
development via reusable packages.

NOTE: WFPM CLI is in active development. More features, documentation and tutorials are coming.


## Best practices for scientific workflow development

* **Reproducible** - same input, same code, same result
  - containerize all software tools (including scripts, binary executables) and specific OS environment
  - tag every image build and associate it with workflow source code release

* **Portable** - run on different platforms, by different users
  - containerize all software tools (containerization appeared again, it is a good friend :blush:)
  - use cross-platform workflow languages and orchestration systems, eg, Nextflow, WDL etc

* **Composable** - enable collaborative development
  - break down big tasks into small tasks (each carried out by a small software tool)
  - one tool per container image
  - version and release independently every tool and its associated container image

* **Findable** - easy to find by research community members
  - register components and workflows in public tool registries, such as Dockstore, BioContainers etc
  - release workflow source code via GitHub Releases

* **Testable** - deliver with high confidence
  - must have tests for every tool, component and workflow
  - configure and enable continuous integration testing


## Prerequisites

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

To show usage information of WFPM CLI, run `wfpm --help`, or simply `wfpm`


## Demo use cases

We present here step-by-step instructions how to use `wfpm` to create Nextflow DSL2 workflow packages.

The packages created by the demo cases can be found at:
[https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs1](https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs1) and
[https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2](https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2) for your reference.

### Demo use case 1: create and publish a demo `tool` package

1. Prepare a GitHub repository under an organization account

Before you start, please make sure you create a repository (with name at your choice, but in the demo let's
use `awesome-wfpkgs1`) under a GitHub organization account (here we use `ICGC-TCGA-PanCancer`).
This is because GitHub Container Registry (GHCR, ghcr.io) is not available for personal account. GHCR is
currently in beta, you need to enable it under your organization profile by: `Settings` =>
`Packages` => `Enable improved container support`. We will be using ghcr.io registry to keep
the container images created and used by the demo tool package.

You also need to create a Personal Access Token (PAT) in order to access GitHub Container Registry,
follow these steps: your account => `Settings` => `Developer settings` => `Personal access tokens` =>
`Generate new token`. Please select `write:packages` scope for the token.

Once PAT is created, please copy the token and add it to the repository you created above. Here are the
steps to go through: `Settings` (under the repository page) => `Secrets` => `New repository secret`.
For name, please use `CR_PAT`, value is the PAT you just created.

GitHub Actions greatly helps continuous integration (CI) and continuous delivery (CD) automation.
CI/CD is an integral part of the workflow package development life cycle. To enable GitHub Actions
for your organization: `Settings` => `Actions` => `Allow all actions`. WFPM CLI generated workflow
package templates include all necessary components to perform CI/CD with no work required from you.


2. Initialize a project directory for developing/managing packages

```
wfpm init
```

Please follow the prompt to provide necessary information. Most important information
includes `github_account` (we use `ICGC-TCGA-PanCancer`) and `project_slug` (this is the project name, and
GitHub repo name, please make sure it matches what you have created at step 1. Here we use `awesome-wfpkgs1`).
Once completed, you should see something similar as below:

```
Project initialized in awesome-wfpkgs1
Git repo initialized and first commit done. When ready, you may push to github.com using:
git push -u origin main
```

When you are ready, as suggested above you can push the code to GitHub. Upon push received at
GitHub, CI/CD process will be automatically triggered.


3. Create your first tool package

```
wfpm new tool fastqc
```

We use the bioinformatics tool `fastqc` as an example here. You
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


4. Publish your first tool package

When you merge the above PR, as part of the comment, you may type a special
instruction `[release]` to let GitHub Actions start the release process, as shown in
the screenshot below. With this GitHub will first merge the `fastqc@0.1.0` branch to the `main` branch,
then starts the release process, once tests are successful, a release of your first tool package
will be made automatically.

![](https://raw.githubusercontent.com/icgc-argo/wfpm/e79611e80f9fc10c728a404fd88798176add5ff7/docs/source/_static/merge-with-release.png)


The release should be available at: [https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs1/releases/tag/fastqc.0.1.0](https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs1/releases/tag/fastqc.0.1.0)
and can be imported and used by anyone (of course including yourself) in their
workflows. How to do that? Please continue to the next demo use case.


### Demo use case 2: create and publish a `workflow` package

In this demo we will be creating a new `workflow` package that makes use of the `fastqc` tool package
we created in demo use case 1 and another utility package published
here: [https://github.com/icgc-argo/demo-wfpkgs/releases/tag/demo-utils.1.1.0](https://github.com/icgc-argo/demo-wfpkgs/releases/tag/demo-utils.1.1.0)

1. Prepare anthor GitHub repository under an organization account

Similar to the first step of demo use case 1, create another repository (here we use `awesome-wfpkgs2`)
in the same GitHub organization, add a PAT to it as a secret and name it `CR_PAT`.

2. Initialize a project directory for developing/managing packages

```
wfpm init
```

Same as in the previous demo, following the prompt to provide necessary information of the new project.
For `github_account` and `project_slug`, we use `ICGC-TCGA-PanCancer` and `awesome-wfpkgs2` respectively
for this demo.

Upon completion, the scaffold of our second project will be generated and first git commit will be done
automatically. You may push the code to GitHub once verified everything is fine.


3. Create your first workflow package

Let's name the first `workflow` package `fastqc-wf`:
```
wfpm new workflow fastqc-wf
```

You may response most of the fields with the default values. Notice that there are dependencies the new
workflow requires:
* `github.com/icgc-tcga-pancancer/awesome-wfpkgs1/fastqc@0.1.0`
* `github.com/icgc-argo/demo-wfpkgs/demo-utils@1.1.0`

Install dependent packages so `fastqc-wf` workflow can import them.

```
wfpm install
```

The follow messages confirm the dependencies are installed properly:

```
Package installed in: wfpr_modules/github.com/icgc-tcga-pancancer/awesome-wfpkgs1/fastqc@0.1.0
Package installed in: wfpr_modules/github.com/icgc-argo/demo-wfpkgs/demo-utils@1.1.0
```

Swith to a new branch named `fastqc-wf@0.1.0`, add the new files to git and push.

```
git checkout -b fastqc-wf@0.1.0
git add .
git commit -m 'added a new workflow fastqc-wf@0.1.0'
git push -u origin fastqc-wf@0.1.0
```

CI/CD process will be triggered on the new branch similar to demo 1. Once tests pass, you may create
a PR as usual.

4. Publish your first workflow package

When merge the PR, type the special instruction `[release]` in the comment (similar as in the previous demo)
to trigger the CI/CD release process via GitHub Actions. Once released, the demo workflow package will be available at: [https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2/releases/tag/fastqc-wf.0.1.0](https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2/releases/tag/fastqc-wf.0.1.0)

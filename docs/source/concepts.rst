Basical Concepts
================

About `WFPM` projects
---------------------

A `WFPM` project is a folder containing necessary `WFPM` configuration and workflow source
code for `WFPM` packages. A project may contain one or more packages.

As workflow source code is typically managed by version control systems, such as, Git.
A source repository may contain one and only one `WFPM` project. The `WFPM` project root
directory is the root directory of its source repository. As such, `WFPM` project shares
the same name as the repository.

The following example shows a typical directory layout of a `WFPM` project. Here the project
is named as ``my-wfpm-project`` (same as the source code repository), which contains one
`WFPM` package named ``demo-package``.

.. code-block:: bash

    my-wfpm-project                      # name of the WFPM project, also the repo name
    ├── .gitignore
    ├── .wfpm                            # WFPM project configuration file
    ├── .github
    │   └── workflows
    │       └── build-test-release.yml   # GitHub Actions code for automated CI/CD
    ├── LICENSE
    ├── LICENSE-short
    ├── README.md
    ├── demo-package                     # folder for the package named 'demo-package'
    │   ├── pkg.json                     # pkg.json keeps basic package info
    │   ├── main.nf                      # package entry script
    │   ├── nextflow.config              # package nextflow default configuration
    │   ├── modules                      # a package may optionally have local modules
    │   │   ├── <local_module_1>
    │   │   └── <local_module_2>
    │   └── tests                        # folder for tests
    │       ├── checker.nf               # test launcher script
    │       └── test-job-1.json          # test job 1
    └── wfpr_modules                     # folder to keep dependent packages
        ├── <dependent_package_1>
        ├── <dependent_package_2>
        └── README.md

The project layout can be generated from the WFMP CLI tool, users don't need to worry about
creating it. More details on creating `WFPM` project and package are available
at `WFPM CLI General Usage`_.

.. _`WFPM CLI General Usage`: usage.html#general-usage

Note that even though a `WFPM` project may contain source code for multiple packages, each
package will be developed, tested and released independently to ensure clean decoupling,
self-sufficiency and portability. More on this can be found at `Package releases`_.


About packages
--------------

A package is a directory, described by a ``pkg.json`` file, containing one or more
modules that can be imported into a workflow codebase. ``pkg.json`` file records basic
information of the package, such as: package name, version, main entry point, source
code repository etc. More information about ``pkg.json`` can be found
at `Create a new tool package`_.

.. _`Create a new tool package`: usage.html#create-a-new-tool-package


A package can be in one of the following formats:

(a) a folder containing a ``pkg.json`` file and necessary workflow script file(s).
(b) a tarball containing (a).
(c) a URL that resolves to (b).
(d) a ``<repo_host_domain>/<repo_name>/<pkg_name>@<version>`` string represents a released package on the source code control server with a release tag ``<pkg_name>.v<version>``. A tarball named ``<pkg_name>.v<version>.tar.gz`` as in (b) is available as a release asset for download.
(e) a ``<repo_host_domain>/<repo_name>/<pkg_name>@<version>_<commit_hash>`` string represents an in-development package on the source code control server with the specified ``commit_hash`` on a branched named ``<pkg_name>@<version>``.

About modules
-------------

A module is a workflow script file that defines one or more of these items:

- A ``tool`` that is a single step of computation. It's known as a ``process`` in Nextflow, a ``tool`` in CWL or a ``task`` in WDL.
- A ``workflow`` that consists of one or more steps of computation, each of the steps is an execution of a ``tool`` described in previous point.
- A ``function`` that takes inputs (in the form of variables: string, number, list, map etc), process them and return a result, which is much the same as functions in any general-purpose programming languages. System built-in functions are supported in Nextflow and WDL, however, only Nextflow supports user-defined functions. 

``tool``, ``workflow`` and ``function`` are referenced by their names and are exposed via the
package's main entry script defined in ``pkg.json`` that ultimately makes them ready to be
imported into another workflow codebase.


Package releases
----------------

Packages are released via facilities provided by source code control systems,
such as `GitHub`_. For common software releases, GitHub allows the user
to choose a release version and write up release note, then it will create
a Git ``tag`` using the release version and generate two default release
assets, ie, source code zip and tarball files.

Since a `WFPM` project source code repository may contain multiple packages,
when a package is being released, only source code artifacts related to the
package to be released should be included in the ``release tarball``. This is
achieved by a package release creation process as part of the GitHub Actions
based continuous delivery (CD). The ``release tarball`` is named as
``<package>.v<version>.tar.gz`` and made available as a release asset.

As another release asset, a ``pkg-release.json`` file is generated. In addition
to information derived from ``pkg.json``, the ``pkg-release.json`` file also
records the Git commit hash from which the release tag was made and the sha256
checksum of the ``release tarball``. For tool packages, the associated container
image sha256 digest is recorded as well. This gives maximized transparency for
reproducibility and safeguard against possible (accidental or deliberate) alteration.

A package release tag is formed by combining package name and version string,
as in ``<package>.v<version>``. This allows a single repository to support
releases of multiple packages without interfering each other.

Note: `semantic versioning`_ is highly recommended for versioning your pacakges.

.. _`GitHub`: https://github.com
.. _`semantic versioning`: https://semver.org


Permissible string patterns for artifact names
----------------------------------------------

+------------------+--------------------------------------------------------------------+
| Artifact         | Pattern                                                            |
+==================+====================================================================+
| *project*        | ``^[a-z][0-9a-z\-]*[0-9a-z]+$``                                    |
+------------------+--------------------------------------------------------------------+
| *package*        | ``^[a-z][0-9a-z\-]*[0-9a-z]+$``                                    |
+------------------+--------------------------------------------------------------------+
| *tool*           | ``^[a-z][0-9a-z]+$``                                               |
+------------------+--------------------------------------------------------------------+
| *workflow*       | ``^[A-Z][0-9a-zA-Z]+$``                                            |
+------------------+--------------------------------------------------------------------+
| *function*       | ``^[a-z][0-9a-z]+$``                                               |
+------------------+--------------------------------------------------------------------+
| *version*        | ``^[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[0-9a-z\.]+)?$``         |
+------------------+--------------------------------------------------------------------+
| *release tag*    | ``<package>.v<version>``                                           |
+------------------+--------------------------------------------------------------------+
| *release tarbal* | ``<package>.v<version>.tar.gz``                                    |
+------------------+--------------------------------------------------------------------+
| *commit hash*    | ``^[0-9a-f]{8,}$``                                                 |
+------------------+--------------------------------------------------------------------+
| *package URI*    | ``<repo_host_domain>/<project>/<package>@<version>``               |
+------------------+--------------------------------------------------------------------+
| *dev package URI*| ``<repo_host_domain>/<project>/<package>@<version>_<commit_hash>`` |
+------------------+--------------------------------------------------------------------+


Dependencies
------------

One of the major design goals of `WFPM` is to support workflow code reuse. Being able
to import code developed by others as dependencies is a native feature in many general-purpoase
programming languages. All `WFPM` packages are uniformly structured and well tested before
releasing. This makes the packages readily importable into other users' codebase. For the
importer side, a package's dependencies can be declared in the ``pkg.json`` file as shown
in the example below:

.. code-block:: json

    "dependencies": [
        "github.com/icgc-argo/data-processing-utility-tools/payload-add-uniform-ids@0.1.1",
        "github.com/icgc-argo/data-processing-utility-tools/helper-functions@1.0.0",
        "github.com/icgc-argo/data-processing-utility-tools/cleanup-workdir@1.0.0"
    ]

Dependent packages are specified using their package URIs. To ensure maximized reproducibility,
`WFPM` requires specifying each dependency to a particular version. 

Dependency installation is fully managed by the `WFPM CLI` tool. Before proceeding with
installation, the CLI tool resolves dependecies (and their dependencies recursively)
to build a complete dependency graph. All dependencies will be installed under ``wfpr_modules``
directory. At runtime, dependencies will be imported from this directory, no need to fetch
from any remote resources.

.. note::
  Fun fact: `WFPM` supports multiple versions of the same package coexist as dependencies,
  thanks to the fact `WFPM` requires importer always explicitly specify a particular version
  of any dependency. In `WFPM`, the well-known `diamond dependency problem`_ is nonexistence.

  Similar approach is taken by Go_: `The need for major version suffixes is one of the ways Go modules differs from most other dependency management systems.`

.. _Go: https://blog.golang.org/v2-go-modules
.. _`diamond dependency problem`: https://www.well-typed.com/blog/2008/04/the-dreaded-diamond-dependency-problem

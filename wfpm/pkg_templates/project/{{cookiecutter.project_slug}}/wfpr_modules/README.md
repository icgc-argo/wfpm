# Workflow Package Installation Directory

This directory contains all dependent workflow packages that are to be installed by the package
management tool: [WFPM](https://github.com/icgc-argo/wfpm) (WorkFlow Package Manager). Please
do NOT modify contents under this directory manually.

Ideally the packages installed in this directory do not need to be checked into git repo, similar
to NPM's `node_modules` directory. Instead, all dependent packages/modules are to be installed
at deployment time. But let's keep the modules checked into git repo before deployment time
installation is supported.

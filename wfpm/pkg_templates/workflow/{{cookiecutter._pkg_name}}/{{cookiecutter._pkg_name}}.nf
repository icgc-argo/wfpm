#!/usr/bin/env nextflow

nextflow.enable.dsl = 2
version = '{{ cookiecutter.pkg_version }}'  // package version

// universal params go here, change default value as needed
params.container_version = ""
params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""  // set to empty string will disable publishDir

// tool specific parmas go here, add / change as needed
params.input_file = ""
params.output_pattern = "*.html"  // fastqc output html report

include { _replace_me_ } from "_replace_me_"


workflow {{ cookiecutter._name }} {
  take:  // input, make update as needed
    input_file

  main:
    _replace_me_(input_file)

  emit:
    output_file = _replace_me_.out.output_file
}

#!/usr/bin/env nextflow

/*
{{ cookiecutter._license_text_short }}
  Authors:
    {{ cookiecutter.full_name }}
*/

nextflow.enable.dsl = 2
version = '{{ cookiecutter.pkg_version }}'  // package version

// universal params go here, change default value as needed
params.container = ""
params.container_registry = ""
params.container_version = ""
params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""  // set to empty string will disable publishDir

// tool specific parmas go here, add / change as needed
params.input_file = ""
params.cleanup = true

// include section starts
include { demoCopyFile } from "./local_modules/demo-copy-file"
// include section ends


// please update workflow code as needed
workflow {{ cookiecutter._name }} {
  take:  // update as needed
    // input section starts
    input_file
    // input section ends

  main:  // update as needed
    // main section starts
    demoCopyFile(input_file)
    // main section ends

  emit:  // update as needed
    // output section starts
    output_file = demoCopyFile.out.output_file
    // output section ends
}


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  {{ cookiecutter._name }}(
    file(params.input_file)
  )
}

#!/usr/bin/env nextflow

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '{{ cookiecutter.pkg_version }}'  // package version

container = [
    '{{ cookiecutter.container_registry }}': '{{ cookiecutter.container_registry }}/{{ cookiecutter.registry_account }}/{{ cookiecutter._repo_name }}.{{ cookiecutter._pkg_name }}'
]
default_container_registry = '{{ cookiecutter.container_registry }}'
/********************************************************************/


// universal params go here
params.container_registry = default_container_registry
params.container_version = ""

params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""  // set to empty string will disable publishDir


// tool specific parmas go here, add / change as needed
params.input_file = ""
params.output_pattern = "*.html"  // fastqc output html report


process {{ cookiecutter._name }} {
  container "${container[params.container_registry]}:${params.container_version ?: version}"
  publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: "${params.publish_dir ? true : ''}"

  cpus params.cpus
  memory "${params.mem} GB"

  input:  // input, make update as needed
    path input_file

  output:  // output, make update as needed
    path "output_dir/${params.output_pattern}", emit: output_file

  script:
    // add and initialize variables here as needed

    """
    mkdir -p output_dir

    {{ cookiecutter._pkg_name }}.py \
      -i ${input_file} \
      -o output_dir

    """
}

#!/usr/bin/env nextflow

/*
 This is an example process as a local module. Using local module is optional, in general
 is discouraged. A process can pentially be reused in different workflows should be developed
 in an independent package, so that it can be imported by anyone into any workflow.
*/

nextflow.enable.dsl = 2

params.input_file = ""
params.publish_dir = ""


process demoCopyFile {
  publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: params.publish_dir

  input:
    path input_file

  output:
    path "output_dir/*", emit: output_file

  script:
    """
    mkdir output_dir
    cp ${input_file} output_dir/
    """
}

#!/usr/bin/env nextflow

/*
 This is an auto-generated checker workflow, please update as needed
*/

nextflow.enable.dsl = 2
version = '{{ cookiecutter.pkg_version }}'  // package version

// universal params
params.publish_dir = ""
params.container_version = ""

// tool specific parmas go here, add / change as needed
params.input_file = ""
params.expected_output = ""

include { {{ cookiecutter._name }} } from '../{{ cookiecutter._pkg_name }}'

Channel
  .fromPath(params.input_file, checkIfExists: true)
  .set { input_file }


process file_diff {
  input:
    path output_file
    path expected_gzip

  output:
    stdout()

  script:
    """
    # remove date field before comparison eg, <div id="header_filename">Tue 19 Jan 2021<br/>test_rg_3.bam</div>
    # sed -e 's#"header_filename">.*<br/>test_rg_3.bam#"header_filename"><br/>test_rg_3.bam</div>#'

    diff <( cat ${output_file} | sed -e 's#"header_filename">.*<br/>test_rg_3.bam#"header_filename"><br/>test_rg_3.bam</div>#' ) \
         <( gunzip -c ${expected_gzip} | sed -e 's#"header_filename">.*<br/>test_rg_3.bam#"header_filename"><br/>test_rg_3.bam</div>#' ) \
    && ( echo "Test PASSED" && exit 0 ) || ( echo "Test FAILED, output file mismatch." && exit 1 )
    """
}


workflow checker {
  take:
    input_file
    expected_output

  main:
    {{ cookiecutter._name }}(
      input_file
    )

    file_diff(
      {{ cookiecutter._name }}.out.output_file,
      expected_output
    )
}


workflow {
  checker(
    file(params.input_file),
    file(params.expected_output)
  )
}

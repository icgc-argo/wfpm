#!/bin/bash

for f in `find . -type d |egrep '(/work$)|(/.nextflow$)|(/outdir$)|(.nextflow.log)'`; do
    echo remove $f;
    rm -fr $f;
done

for f in `find . -type f |egrep '\.nextflow\.log'`; do
    echo remove $f;
    rm $f;
done


#!/usr/bin/sh

python3 -m coolisf.gold_extract
cd data
tar -zcvf spec-isf.xml.tar.gz spec-isf.xml

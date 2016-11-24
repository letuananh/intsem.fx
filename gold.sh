#!/usr/bin/sh

python3 -m coolisf.main gold
cd data
tar -zcvf spec-isf.xml.tar.gz spec-isf.xml

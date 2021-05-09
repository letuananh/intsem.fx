#!/bin/bash

python3 -W ignore -m isftk.ttl cmp -g data/semeval/gold.ttl.json.gz -p data/semeval/semeval_isf_lesk.ttl.json.gz --debug data/semeval/semeval_isf_lesk_debug.txt --ignore data/semeval/semeval_isf_lesk_noparse.txt --nonsense -q --ttl_format json --batch --org --cols "ISF/LESK"
python3 -W ignore -m isftk.ttl cmp -g data/semeval/gold.ttl.json.gz -p data/semeval/semeval_isf_mfs.ttl.json.gz --debug data/semeval/semeval_isf_mfs_debug.txt --ignore data/semeval/semeval_isf_mfs_noparse.txt --nonsense -q --ttl_format json --org --batch --cols "ISF/MFS"
python3 -W ignore -m isftk.ttl cmp -g data/semeval/gold.ttl.json.gz -p data/semeval/semeval_ace_lesk.ttl.json.gz --debug data/semeval/semeval_ace_lesk_debug.txt --ignore data/semeval/semeval_ace_lesk_noparse.txt --nonsense -q --ttl_format json --batch --org --cols "ACE/LESK"
python3 -W ignore -m isftk.ttl cmp -g data/semeval/gold.ttl.json.gz -p data/semeval/semeval_ace_mfs.ttl.json.gz --debug data/semeval/semeval_ace_mfs_debug.txt --ignore data/semeval/semeval_ace_mfs_noparse.txt --nonsense -q --ttl_format json --batch --cols "ACE/MFS" --org
python3 -W ignore -m isftk.ttl cmp -g data/semeval/gold.ttl.json.gz -p data/semeval/semeval_ukb.ttl.json.gz --debug data/semeval/semeval_ukb_debug.txt --nonsense -q --ttl_format json --org --batch --cols "UKB"


#!/bin/bash

echo "| Profile         | Tokenizer | Recall | Precision |     F1 |"
echo "|-----------------+-----------+--------+-----------+--------|"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ukb/speckled_r26463_isf_ukb.ttl.json.gz --ignore data/ukb/speckled_r26463_isf_ukb_noparse.txt --debug data/ukb/speckled_r26463_isf_ukb_debug.txt --ttl_format json --nonsense -q --batch --org --cols "Dan/ISF/UKB" "Dan/ISF"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ukb/speckled_ro26463_isf_ukb.ttl.json.gz --ignore data/ukb/speckled_ro26463_isf_ukb_noparse.txt --debug data/ukb/speckled_ro26463_isf_ukb_debug.txt --ttl_format json --nonsense -q --batch --org --cols "DanRo/ISF/UKB" "DanRo/ISF"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_isf_lesk.ttl.json.gz --debug data/ace/silver_isf_lesk_debug.txt --ignore data/ace/silver_isf_lesk_noparse.txt -q --nonsense --batch --org --cols "ERG/ISF" "ERG/ISF"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_lesk.ttl.json.gz --debug data/ace/silver_lesk_debug.txt --ignore data/ace/silver_lesk_noparse.txt -q --nonsense --batch --org --cols "ERG" "ERG"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_bb_wn.ttl.json.gz --debug data/shallow/speckled_bb_wn_debug.txt --ttl_format json --nonsense -q --batch --org --cols "Babelfy" "Babelfy"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_ukb.ttl.json.gz --debug data/shallow/speckled_ukb_debug.txt --ttl_format json --nonsense -q --batch --org --cols "UKB" "Stanford"

echo ""
echo "*LESK - Best of each*"
echo "| Profile         | Tokenizer | Recall | Precision |     F1 |"
echo "|-----------------+-----------+--------+-----------+--------|"
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_ro26463_isf_lesk.ttl.json.gz --debug data/isf/speckled_ro26463_isf_lesk_debug.txt -q --ignore data/isf/speckled_ro26463_isf_lesk_noparse.txt --nonsense  --batch --org --cols "Dan/bridge/ISF" "Dan/bridge/ISF" --batch --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_r26463_isf_lesk.ttl.json.gz --debug data/isf/speckled_r26463_isf_lesk_debug.txt -q --ignore data/isf/speckled_r26463_isf_lesk_noparse.txt --nonsense --batch --org --cols "Dan/ISF" "Dan/ISF"  --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_ro26463_lesk.ttl.json.gz --debug data/isf/speckled_ro26463_lesk_debug.txt -q --ignore data/isf/speckled_ro26463_lesk_noparse.txt --nonsense --batch --org --cols "Dan/bridge" "Dan/bridge"  --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_r26463_lesk.ttl.json.gz --debug data/isf/speckled_r26463_lesk_debug.txt -q --ignore data/isf/speckled_r26463_lesk_noparse.txt --nonsense --batch --org --cols "Dan" "Dan"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_isf_lesk.ttl.json.gz --debug data/ace/silver_isf_lesk_debug.txt --ignore data/ace/silver_isf_lesk_noparse.txt -q --nonsense --batch --org --cols "ERG/ISF" "ERG/ISF"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_lesk.ttl.json.gz --debug data/ace/silver_lesk_debug.txt --ignore data/ace/silver_lesk_noparse.txt -q --nonsense --batch --org --cols "ERG" "ERG"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_lesk.ttl.json.gz --debug data/shallow/speckled_lesk_debug.txt --ttl_format json --nonsense -q --batch --org --cols "NLTK" "NLTK"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_stanford_lesk.ttl.json.gz --debug data/shallow/speckled_stanford_lesk_debug.txt --nonsense -q --batch --org --cols "Stanford tagger" "Stanford tagger"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_ukb.ttl.json.gz --debug data/shallow/speckled_ukb_debug.txt --ttl_format json --nonsense -q --batch --org --cols "UKB" "Stanford"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_bb_wn.ttl.json.gz --debug data/shallow/speckled_bb_wn_debug.txt --ttl_format json --nonsense -q --batch --org --cols "Babelfy" "Babelfy"

echo ""
echo "*MFS - Best of each*"
echo "| Profile         | Recall | Precision |     F1 |"
echo "|-----------------+--------+-----------+--------|"
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_ro26463_isf_mfs.ttl.json.gz --debug data/isf/speckled_ro26463_isf_mfs_debug.txt -q --ignore data/isf/speckled_ro26463_noparse.txt --nonsense  --batch --org --cols "Dan/bridge/ISF" "Dan/bridge/ISF" --batch --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_r26463_isf_mfs.ttl.json.gz --debug data/isf/speckled_r26463_isf_mfs_debug.txt -q --ignore data/isf/speckled_r26463_noparse.txt --nonsense --batch --org --cols "Dan/ISF" "Dan/ISF"  --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_ro26463_mfs.ttl.json.gz --debug data/isf/speckled_ro26463_mfs_debug.txt -q --ignore data/isf/speckled_ro26463_noparse.txt --nonsense --batch --org --cols "Dan/bridge" "Dan/bridge"  --ttl_format json
python -W ignore -m isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/isf/speckled_r26463_mfs.ttl.json.gz --debug data/isf/speckled_r26463_mfs_debug.txt -q --ignore data/isf/speckled_r26463_noparse.txt --nonsense --batch --org --cols "Dan" "Dan"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_isf_mfs.ttl.json.gz --debug data/ace/silver_isf_mfs_debug.txt --ignore data/ace/silver_isf_mfs_noparse.txt -q --nonsense --batch --org --cols "ERG/ISF" "ERG/ISF"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/ace/silver_mfs.ttl.json.gz --debug data/ace/silver_mfs_debug.txt --ignore data/ace/silver_mfs_noparse.txt -q --nonsense --batch --org --cols "ERG" "ERG"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_mfs.ttl.json.gz --debug data/shallow/speckled_mfs_debug.txt --ttl_format json --nonsense -q --batch --org --cols "NLTK" "NLTK"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_stanford_mfs.ttl.json.gz --debug data/shallow/speckled_stanford_mfs_debug.txt --nonsense -q --batch --org --cols "Stanford tagger" "Stanford tagger"  --ttl_format json
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_ukb.ttl.json.gz --debug data/shallow/speckled_ukb_debug.txt --ttl_format json --nonsense -q --batch --org --cols "UKB" "Stanford"
python -W ignore -m  isftk.ttl cmp -g data/gold/gold_imi.ttl.json.gz -p data/shallow/speckled_bb_wn.ttl.json.gz --debug data/shallow/speckled_bb_wn_debug.txt --ttl_format json --nonsense -q --batch --org --cols "Babelfy" "Babelfy"

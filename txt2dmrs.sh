#!/usr/bin/sh

########################################################################
# CONFIGURATION
########################################################################
DATA_DIR=./data
GRAMFILE=${DATA_DIR}/erg2.dat
INFILE=${DATA_DIR}/speckled.txt
OUTFILE=${DATA_DIR}/speckled.out
TOP_K=1

if [ $# -eq 2 ]; then
	INFILE=$1
	OUTFILE=$2
fi

if   [ ! -f "${INFILE}" ]; then
	echo "Input file doesn't exist. >>> ${INFILE} <<<"
elif [ ! -f "${OUTFILE}" ]; then
	ace -g ${GRAMFILE} --tnt-model ~/logon/coli/tnt/models/wsj.tnt "${INFILE}" --max-chart-megabytes=4000 --max-unpack-megabytes=4000 -T -n ${TOP_K} > "${OUTFILE}"
else
	echo "Output file exists! >>> ${OUTFILE} <<<"
fi

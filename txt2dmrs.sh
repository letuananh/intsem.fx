#!/usr/bin/sh

########################################################################
# CONFIGURATION
########################################################################
DATA_DIR=./data
GRAMFILE=${DATA_DIR}/erg.dat
INFILE=${DATA_DIR}/semcor.txt
OUTFILE=${DATA_DIR}/semcor.out
TOP_K=10

if [ $# -eq 2 ]; then
	INFILE=$1
	OUTFILE=$2
fi

if   [ ! -f "${INFILE}" ]; then
	echo "Input file doesn't exist. >>> ${INFILE} <<<"
elif [ ! -f "${OUTFILE}" ]; then
	ace -g ${GRAMFILE} "${INFILE}" -T -n ${TOP_K} > "${OUTFILE}"
else
	echo "Output file exists! >>> ${OUTFILE} <<<"
fi

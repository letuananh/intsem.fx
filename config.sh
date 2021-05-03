#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)
WORKSPACE_FOLDER=~/workspace
py3=`python -c "import sys; print('1' if sys.version_info >= (3,0) else '0')"`

function link_folder {
    FOLDER_PATH=$1
    SYMLINK_NAME=$2
    if [ ! -d ${FOLDER_PATH} ]; then
        echo "WARNING: Target folder ${bold}${FOLDER_PATH}${normal} does not exist"
    elif [ ! -d ${SYMLINK_NAME} ]; then
	ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
    else
	echo "Folder ${bold}${SYMLINK_NAME}${normal} exists."
    fi
}

function link_file {
    TARGET_FILE=$1
    SYMLINK_NAME=$2
    if [ ! -f ${TARGET_FILE} ]; then
        echo "WARNING: Target file ${bold}${TARGET_FILE}${normal} does not exist"
    elif [ ! -f ${SYMLINK_NAME} ]; then
	ln -sv ${TARGET_FILE} ${SYMLINK_NAME}
    else
	echo "File ${bold}${SYMLINK_NAME}${normal} exists."
    fi
}

if [ ${py3} -eq 0 ]; then
    echo "+-------------------------------+"
    echo "| WARNING: Python 3 is required |"
    echo "+-------------------------------+"
fi

# init submodules
git submodule init && git submodule update

# prerequisite packages
pip install -r requirements.txt -qq

link_folder `readlink -f ./modules/lelesk/lelesk` lelesk
link_folder `readlink -f ./modules/demophin` demophin
link_folder `readlink -f ./modules/yawlib/yawlib` yawlib

link_file `readlink -f ${WORKSPACE_FOLDER}/cldata/erg.dat` data/erg.dat
link_file `readlink -f ${WORKSPACE_FOLDER}/cldata/jacy.dat` data/jacy.dat
link_file `readlink -f ${WORKSPACE_FOLDER}/cldata/virgo.dat` data/virgo.dat

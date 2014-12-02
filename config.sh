#!/usr/bin/sh

function link_folder {
	FOLDER_PATH=$1
	SYMLINK_NAME=$2
	if [ ! -d ${SYMLINK_NAME} ]; then
		ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
	else
		echo "Folder ${SYMLINK_NAME} exists."
	fi
}

function link_file {
	FOLDER_PATH=$1
	SYMLINK_NAME=$2
	if [ ! -f ${SYMLINK_NAME} ]; then
		ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
	else
		echo "File ${SYMLINK_NAME} exists."
	fi
}

link_folder ~/workspace/pydelphin/delphin delphin
link_folder ~/workspace/beautifulsoup/bs4-python3 bs4
link_folder ~/workspace/nltk/nltk nltk
link_file ~/workspace/erg/erg.dat data/erg.dat

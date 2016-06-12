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

# Where you check out projects to
WORKSPACE_FOLDER=~/workspace

link_folder `readlink -f ${WORKSPACE_FOLDER}/pydelphin/delphin` delphin
link_folder `readlink -f ${WORKSPACE_FOLDER}/beautifulsoup/bs4-python3` bs4
link_folder `readlink -f ${WORKSPACE_FOLDER}/nltk/nltk` nltk

link_folder `readlink -f ./modules/chirptext/chirptext` chirptext
link_folder `readlink -f ./modules/lelesk/lelesk` lelesk
link_folder `readlink -f ./modules/demophin` demophin
link_folder `readlink -f ./modules/puchikarui/puchikarui` puchikarui

echo "Configuring lelesk"
./modules/lelesk/config.sh

link_file `readlink -f ${WORKSPACE_FOLDER}/erg/erg.dat` data/erg.dat

git submodule init && git submodule update

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

link_folder `readlink -f ../pydelphin/delphin` delphin
link_folder `readlink -f ../beautifulsoup/bs4-python3` bs4
link_folder `readlink -f ../nltk/nltk` nltk

link_folder `readlink -f ./modules/chirptext/chirptext` chirptext
link_folder `readlink -f ./modules/lelesk/lelesk` lelesk
link_folder `readlink -f ./modules/demophin` demophin

echo "Configuring lelesk"
./modules/lelesk/config.sh

link_file `readlink -f ~/workspace/erg/erg.dat` data/erg.dat

git submodule init && git submodule update

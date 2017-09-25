#!/bin/bash

export PROJECT_ROOT=`pwd`
export BUILD_DIR=${PROJECT_ROOT}/build
export RELEASE_DIR=${PROJECT_ROOT}/release

function create_dir {
    FOLDER_NAME=$1
    if [ ! -d ${FOLDER_NAME} ]; then
        mkdir ${FOLDER_NAME}
    fi
}

# Find current branch
CURRENT=`git branch | grep '\*' | awk ' {print $2}'`

# Export current branch to build directory

rm -rf ${BUILD_DIR}
rm -rf ${RELEASE_DIR}
create_dir ${BUILD_DIR}
git archive ${CURRENT} | tar -x -C ${BUILD_DIR}

git submodule update
git submodule foreach --recursive 'git archive --verbose HEAD | tar -x -C ${BUILD_DIR}/$path'


# Copy required files to release directory
create_dir ${RELEASE_DIR}
cp -rfv ${BUILD_DIR}/modules/chirptext/chirptext ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/modules/lelesk/lelesk ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/modules/puchikarui/puchikarui ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/modules/yawlib/yawlib ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/data ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/coolisf ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/isf ${RELEASE_DIR}/

cp -rfv ${BUILD_DIR}/setup.py ${RELEASE_DIR}/

cp -rfv ${BUILD_DIR}/LICENSE ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/requirements.txt ${RELEASE_DIR}/
cp -rfv ${BUILD_DIR}/README.md ${RELEASE_DIR}/

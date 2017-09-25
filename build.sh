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

create_dir ${BUILD_DIR}
create_dir ${RELEASE_DIR}

# Export current branch to build directory

export ISF_BUILD=${BUILD_DIR}/isf
export ISF_RELEASE=${RELEASE_DIR}/isf

# clean old builds
rm -rf ${ISF_BUILD}
rm -rf ${ISF_RELEASE}

# release ISF
create_dir ${ISF_BUILD}
git archive ${CURRENT} | tar -x -C ${ISF_BUILD}
# release submodules
git submodule update
git submodule foreach --recursive 'git archive --verbose HEAD | tar -x -C ${ISF_BUILD}/$path'

# Copy required files to release directory
create_dir ${ISF_RELEASE}
cp -rfv ${ISF_BUILD}/modules/chirptext/chirptext ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/modules/lelesk/lelesk ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/modules/puchikarui/puchikarui ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/modules/yawlib/yawlib ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/data ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/coolisf ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/isf ${ISF_RELEASE}/

cp -rfv ${ISF_BUILD}/setup.py ${ISF_RELEASE}/

cp -rfv ${ISF_BUILD}/LICENSE ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/requirements.txt ${ISF_RELEASE}/
cp -rfv ${ISF_BUILD}/README.md ${ISF_RELEASE}/

cd ${RELEASE_DIR}
tar -zcvf isf.tar.gz isf
ls -l ${RELEASE_DIR}

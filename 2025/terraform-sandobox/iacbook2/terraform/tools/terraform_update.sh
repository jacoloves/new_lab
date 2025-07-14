#!/bin/sh

ROOTDIR=$(cd "$(dirname $0)"/.. && pwd)
VERSION="$(tfupdate release latest hashicorp/terraform)"
tfupdate terraform --recursive --version "${VERSION}" "${ROOTDIR}/env"
find "${ROOTDIR}/env" -name ".terraform-version" -print0 | xargs -0 -I{} sh -c "echo ${VERSION} > {}"

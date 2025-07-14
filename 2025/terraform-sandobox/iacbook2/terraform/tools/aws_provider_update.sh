#!/bin/sh

ROOTDIR=$(cd "$(dirname $0)"/.. && pwd)
VERSION="$(tfupdate release latest hashicorp/terraform-provider-aws)"
tfupdate provider aws --recursive --version "${VERSION}" "${ROOTDIR}/env"
tfupdate lock --recursive --platform=linux_amd64 --platform=darwin_arm64 "${ROOTDIR}/env"

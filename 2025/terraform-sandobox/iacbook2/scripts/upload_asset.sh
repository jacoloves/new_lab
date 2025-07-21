#!/bin/sh

set -e

LAMBDA_NAME=${1:?}
ZIPFILE_INPUT=${2:?}
STAGE=${3:-dev}

BUCKET="${STAGE}-lambda-assets-iac-book-project-shooonng-20250720"

SHA256HASH=$(sha256sum "${ZIPFILE_INPUT}" | cut -d ' ' -f 1)

ZIPFILE_BASENAME="${SHA256HASH}.zip"
set +e
aws s3api head-object --bucket "${BUCKET}" --key "${LAMBDA_NAME}/${ZIPFILE_BASENAME}" > /dev/null 2>&1
RC=$?
set -e
if [ ${RC} -eq 0 ]; then
    echo "The object s3://${BUCKET}/${LAMBDA_NAME}/${ZIPFILE_BASENAME} already exists."
    echo "Failed to upload the zip file to S3."
    exit 1
elif [ ${RC} -ne 254 ]; then
    echo "Failed to check the existence of the object s3://${BUCKET}/${LAMBDA_NAME}/${ZIPFILE_BASENAME}."
    exit 1
fi

aws s3 cp "${ZIPFILE_INPUT}" "s3://${BUCKET}/${LAMBDA_NAME}/${ZIPFILE_BASENAME}"

aws ssm put-parameter --name "/lambda-zip/${STAGE}/${LAMBDA_NAME}" --value "${SHA256HASH}" --type String --overwrite

exit 0
#!/bin/sh

TERRAFORM_VERSION="1.9.8"
AWS_PROVIDER_VERSION="5.72.1"
BUCKET_SUFFIX="iac-book-project"

if [ $# -ne 2 ]; then
	echo "Usage: $0 <stage> <module_name>"
	exit 1
fi

STAGE=$1
MODULE_NAME=$2

ROOTDIR=$(cd "$(dirname $0)"/.. && pwd)
BACKEND_BUCKET_NAME="${STAGE}-tfstate-aws-${BUCKET_SUFFIX}"

if [ "${STAGE}" = "modules" ] || [ "${STAGE}" = "usecases" ]; then
	MODULE_FLAG=1
	WDIR=${ROOTDIR}/${STAGE}/${MODULE_NAME}
	VERSION_OPERATOR=""
else
	MODULE_FLAG=0
	WDIR=${ROOTDIR}/env/${STAGE}/${MODULE_NAME}
	VERSION_OPERATOR=""
fi
mkdir -p ${WDIR}
cd ${WDIR} || exit 1

cat <<EOF >terraform.tf
terraform {
  required_version = "${VERSION_OPERATOR}${TERRAFORM_VERSION}"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "${VERSION_OPERATOR}${AWS_PROVIDER_VERSION}"
    }
  }
}
EOF

if [ ${MODULE_FLAG} -ne 1 ]; then
	cat <<EOF >.terraform-version
${TERRAFORM_VERSION}
EOF

	cat <<EOF >backend.tf
terraform {
  backend "s3" {
    bucket = "${BACKEND_BUCKET_NAME}"
    key    = "${MODULE_NAME}/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
EOF

	cat <<EOF >provider.tf
provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = {
      Terraform = "true"
      STAGE     = "${STAGE}"
      MODULE    = "${MODULE_NAME}"
    }
  }
}

provider "aws" {
  alias  = "us_east_1"
  region = "us_east_1"
  degault_tags {
    tags = {
      Terraform = "true"
      STAGE     = "${STAGE}"
      MODULE    = "${MODULE_NAME}"
    }
  }
}
EOFj
fi

touch main.tf
touch output.tf
touch locals.tf
touch data.tf

if [ ${MODULE_FLAG} -eq 1 ]; then
  touch variables.tf
fi

echo "Files are created in ${WDIR}"

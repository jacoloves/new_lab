locals {
  domain                             = "https://token.actions.githubusercontent.com"
  openid_provider_configuration_path = "/.well-known/openid-configuration"
  openid_configuration_url           = "${local.domain}${local.openid_provider_configuration_path}"
}

data "http" "openid_configuration" {
  url = local.openid_configuration_url
}

data "tls_certificate" "encryption_key" {
  url = jsondecode(data.http.openid_configuration.response_body).jwks_uri
}

resource "aws_iam_openid_connect_provider" "github" {
  url = local.domain
  client_id_list = [
    "sts.amazonaws.com"
  ]
  thumbprint_list = [
    data.tls_certificate.encryption_key.certificates[0].sha1_fingerprint
  ]
}

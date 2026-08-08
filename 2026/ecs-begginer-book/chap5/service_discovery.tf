resource "aws_service_discovery_private_dns_namespace" "sbcntr" {
  name        = "sbcntr.local"
  description = "sbcntr local namespace for ECS services"
  vpc         = aws_vpc.main.id
}

resource "aws_service_discovery_service" "backend_app" {
  name        = "backend-app"
  description = "Backend App Service"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.sbcntr.id

    dns_records {
      type = "A"
      ttl  = 10
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }

  # 名前変更で置き換えが発生する際、ECSサービスが新しい方へ登録し直してから
  # 古い方(インスタンス登録が空になった状態)を削除する順序にするため
  lifecycle {
    create_before_destroy = true
  }
}

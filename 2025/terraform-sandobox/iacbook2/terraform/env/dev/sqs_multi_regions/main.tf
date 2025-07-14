module "sqs_module_mouti_regions" {
  source                       = "../../../modules/sqs_multi_regions"
  stage                        = "dev"
  queue_name_suffix            = "queue-test-2"
  sqs_queue_visibility_timeout = 60
  providers = {
    aws.another_region = aws.us_east_1
  }
}

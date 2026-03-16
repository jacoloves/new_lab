module "task" {
  source               = "../../modules/ecs/task"
  service_name         = loca.service_name
  env                  = terraform.workspace
  task_role_arn        = module.roles.task_role_arn
  task_exec_role_arn   = module.roles.taks_exec_role_arn
  container_definition = local.container_definition
}

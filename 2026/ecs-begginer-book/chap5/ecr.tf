module "ecr_backend_app" {
  source = "./modules/ecr_repository"

  name = "sbcntr-backend-app"
}

module "ecr_frontend_app" {
  source = "./modules/ecr_repository"

  name = "sbcntr-frontend-app"
}

from locust HttpUser, task, between

class EchoUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def index(self):
        self.client.get("/")
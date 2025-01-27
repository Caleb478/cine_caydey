from locust import HttpUser, task, between

# FUNCION PARA LA PRUEBA DE TESTING
class CineAppUser(HttpUser):
    wait_time = between(1, 5)  # Espera entre 1 y 5 segundos entre tareas

    @task
    def view_homepage(self):
        self.client.get("/")  # Prueba la página de inicio

    @task
    def login(self):
        self.client.post("/login", {
            "usuario": "test_user",
            "contrasena": "test_password"
        })  # Prueba el inicio de sesión

    @task
    def obtener_peliculas(self):
        self.client.get("/obtener_peliculas")  # Prueba la obtención de películas

    @task
    def obtener_sesiones(self):
        self.client.get("/sesiones/1")  # Prueba la obtención de sesiones para una película específica
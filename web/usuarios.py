from werkzeug.security import check_password_hash, generate_password_hash


class RepositorioUsuarios:
    """Alta y login de usuarios. La persistencia la resuelve el repositorio."""

    def __init__(self, repo):
        self._repo = repo

    def registrar(self, nombre: str, email: str, password: str) -> None:
        email = email.strip().lower()
        if not nombre.strip() or not email or not password:
            raise ValueError("Completá todos los campos")
        if "@" not in email:
            raise ValueError("El email no es válido")
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        if not self._repo.crear_usuario(nombre.strip(), email, generate_password_hash(password)):
            raise ValueError("Ya existe un usuario con ese email")

    def asegurar_usuario_demo(self) -> None:
        if not self._repo.obtener_usuario("demo@ecoharmony.com"):
            self._repo.crear_usuario(
                "Visitante Demo", "demo@ecoharmony.com", generate_password_hash("demo123")
            )

    def autenticar(self, email: str, password: str):
        usuario = self._repo.obtener_usuario(email.strip().lower())
        if usuario and check_password_hash(usuario["password"], password):
            return usuario
        return None

    def obtener(self, email: str):
        return self._repo.obtener_usuario(email)

from dotenv import load_dotenv

load_dotenv()  # lee .env antes de crear la app; en Vercel las variables ya vienen cargadas

from web import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    print("EcoHarmony Park corriendo en http://localhost:5001")
    print("Para comprar, creá una cuenta en /registro")
    app.run(debug=True, port=5001)

from web import create_app

app = create_app()

if __name__ == "__main__":
    print("EcoHarmony Park corriendo en http://localhost:5000")
    print("Usuario de prueba: demo@ecoharmony.com / demo123")
    app.run(debug=True, port=5000)

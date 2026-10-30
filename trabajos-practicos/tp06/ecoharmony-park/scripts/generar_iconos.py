"""Regenera los íconos rasterizados a partir de los SVG del logo.

    python scripts/generar_iconos.py

- web/static/logo-icono.svg -> favicon.ico (16, 32 y 48 px) y apple-touch-icon.png (180 px)
- web/static/logo.svg       -> logo-mail.png (los clientes de mail no muestran SVG)

Usa Chrome (headless) para rasterizar el SVG y Pillow para armar el .ico.
Correlo cada vez que reemplaces logo.svg o logo-icono.svg.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTATICOS = os.path.join(RAIZ, "web", "static")
CREMA = (0xF2, 0xE8, 0xCF, 255)

CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def chrome() -> str:
    for ruta in CHROMES:
        if ruta and os.path.exists(ruta):
            return ruta
    sys.exit("No encontré Chrome/Chromium para rasterizar los SVG.")


def rasterizar(svg: str, lado: int) -> Image.Image:
    """Renderiza el SVG centrado en un cuadrado transparente de lado x lado."""
    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, "a.html")
        png = os.path.join(tmp, "a.png")
        with open(html, "w") as f:
            f.write(f'<body style="margin:0"><img src="file://{svg}" width="{lado}" height="{lado}" '
                    f'style="display:block;object-fit:contain"></body>')
        ventana = max(lado, 500)  # Chrome headless no baja de 500 px
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--default-background-color=00000000",
                        f"--window-size={ventana},{ventana}", f"--screenshot={png}", f"file://{html}"],
                       check=True, capture_output=True)
        return Image.open(png).convert("RGBA").crop((0, 0, lado, lado))


def main():
    icono = os.path.join(ESTATICOS, "logo-icono.svg")
    logo = os.path.join(ESTATICOS, "logo.svg")

    # favicon.ico: varios tamaños, renderizados a 4x y reducidos (bordes más limpios)
    grande = rasterizar(icono, 256)
    grande.save(os.path.join(ESTATICOS, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    # apple-touch-icon: iOS no usa transparencia, así que va sobre crema con margen
    lienzo = Image.new("RGBA", (180, 180), CREMA)
    hoja = rasterizar(icono, 150)
    lienzo.alpha_composite(hoja, (15, 15))
    lienzo.convert("RGB").save(os.path.join(ESTATICOS, "apple-touch-icon.png"))

    # logo para el mail: 96 px de alto en pantalla, generado a 2x para pantallas retina
    rasterizar(logo, 192).save(os.path.join(ESTATICOS, "logo-mail.png"), optimize=True)
    print("Listo: favicon.ico, apple-touch-icon.png y logo-mail.png en web/static/")


if __name__ == "__main__":
    main()

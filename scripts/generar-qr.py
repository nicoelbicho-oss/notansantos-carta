"""
Genera QR codes en alta resolución para la carta de No Tan Santos.

Salidas:
  qr/QR-NoTanSantos-{tamaño}-{variante}.png

Variantes:
  - puro      → QR negro/blanco sin logo (más fácil de escanear, el más seguro)
  - logo      → QR con el logo NTS embebido en el centro

Tamaños:
  - 600       → 600x600 px (chico, ~3-4 cm impreso)
  - 1000      → 1000x1000 px (mediano, ~5-7 cm)
  - 1500      → 1500x1500 px (mediano-grande)
  - 2000      → 2000x2000 px (alta resolución, para cualquier tamaño de impresión)

Uso:
  python scripts/generar-qr.py
"""
import os
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "referencias" / "logo.png.png"
OUT_DIR = ROOT / "qr"
OUT_DIR.mkdir(exist_ok=True)

URL = "https://notansantos-carta.vercel.app/"
TAMANOS = [600, 1000, 1500, 2000]

# Colores oficiales
NEGRO = "#0a0a0a"   # Negro suave, no plano puro (lee igual de bien)
BLANCO = "#ffffff"


def hacer_qr_base(size_px: int) -> Image.Image:
    """QR sin logo, fondo blanco, negro. Tamaño final size_px x size_px."""
    qr = qrcode.QRCode(
        version=None,                    # auto-fit
        error_correction=ERROR_CORRECT_H,  # 30% de redundancia, aguanta el logo
        box_size=20,
        border=4,                        # quiet zone (4 módulos = estándar)
    )
    qr.add_data(URL)
    qr.make(fit=True)

    img = qr.make_image(fill_color=NEGRO, back_color=BLANCO).convert("RGB")
    return img.resize((size_px, size_px), Image.NEAREST)


def pegar_logo(qr_img: Image.Image, logo_pct_ancho: float = 0.26) -> Image.Image:
    """
    Pega el logo NTS en el centro del QR.
    logo_pct_ancho = ancho del logo como fracción del ancho del QR.
    Agrega un margen blanco alrededor para que el scanner lea bien.
    """
    qr_w, qr_h = qr_img.size

    # Cargar logo
    logo = Image.open(LOGO_PATH).convert("RGBA")

    # Escalar logo (mantiene aspect ratio del cartel original)
    logo_w = int(qr_w * logo_pct_ancho)
    logo_h = int(logo_w * logo.height / logo.width)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    # Crear un marco blanco un poco más grande que el logo para legibilidad
    padding = int(qr_w * 0.012)
    marco_w = logo_w + padding * 2
    marco_h = logo_h + padding * 2
    marco = Image.new("RGBA", (marco_w, marco_h), (255, 255, 255, 255))

    # Pegar logo (centrado) sobre el marco blanco
    marco.paste(logo, (padding, padding), logo)

    # Pegar todo el marco sobre el QR
    qr_copia = qr_img.copy()
    pos_x = (qr_w - marco_w) // 2
    pos_y = (qr_h - marco_h) // 2
    qr_copia.paste(marco, (pos_x, pos_y), marco)
    return qr_copia


def generar(tamano: int):
    """Genera dos variantes (puro + logo) para un tamaño dado."""
    base = hacer_qr_base(tamano)

    # Variante 1: puro
    puro_path = OUT_DIR / f"QR-NoTanSantos-{tamano}-puro.png"
    base.save(puro_path, "PNG", optimize=True)
    print(f"  [OK] {puro_path.name}")

    # Variante 2: con logo
    con_logo = pegar_logo(base)
    logo_path = OUT_DIR / f"QR-NoTanSantos-{tamano}-logo.png"
    con_logo.save(logo_path, "PNG", optimize=True)
    print(f"  [OK] {logo_path.name}")


def main():
    print(f"Generando QRs para: {URL}")
    print(f"Logo:    {LOGO_PATH}")
    print(f"Salida:  {OUT_DIR}\n")

    for tamano in TAMANOS:
        print(f"Tamaño {tamano}x{tamano}:")
        generar(tamano)

    print(f"\nListo. {len(TAMANOS) * 2} archivos generados en {OUT_DIR}/")


if __name__ == "__main__":
    main()

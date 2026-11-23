"""

Uso:  python subir_archivos.py
"""
import re
import sys
import unicodedata
from pathlib import Path

import requests

API = "http://127.0.0.1:8000"
BASE = Path(__file__).resolve().parent / "materiales"

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp"}
EXT_AUDIO = {".mp3", ".wav", ".ogg"}


def normalizar(texto: str) -> str:
    """'Árbol' -> 'arbol' (misma regla que usa el backend)."""
    t = unicodedata.normalize("NFD", texto.strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def indexar(carpeta: Path, extensiones: set) -> dict:
    """{'perro': Path('.../perro.jpg'), ...}"""
    if not carpeta.exists():
        return {}
    return {p.stem.lower(): p for p in carpeta.iterdir() if p.suffix.lower() in extensiones}


def main():
    try:
        r = requests.get(f"{API}/api/elementos", timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f"No se pudo conectar con la API ({e}). ¿Está corriendo uvicorn?")

    elementos = r.json()
    imagenes = indexar(BASE / "imagenes", EXT_IMAGEN)
    audios = indexar(BASE / "audios", EXT_AUDIO)
    print(f"{len(elementos)} elementos en la BD | {len(imagenes)} imágenes | {len(audios)} audios\n")

    subidos = sin_nada = errores = 0
    for e in elementos:
        slug = normalizar(e["nombre_espanol"])
        candidatos = {
            "imagen": imagenes.get(slug),
            "audio_mazahua": audios.get(f"{slug}_mazahua"),
            "audio_espanol": audios.get(f"{slug}_espanol"),
        }
        candidatos = {campo: ruta for campo, ruta in candidatos.items() if ruta}

        if not candidatos:
            print(f"  -  {e['nombre_espanol']}: no hay archivos en material/")
            sin_nada += 1
            continue

        abiertos = {campo: ruta.open("rb") for campo, ruta in candidatos.items()}
        try:
            resp = requests.put(
                f"{API}/api/elementos/{e['id']}",
                files={campo: (ruta.name, abiertos[campo]) for campo, ruta in candidatos.items()},
                timeout=60,
            )
        finally:
            for f in abiertos.values():
                f.close()

        if resp.ok:
            print(f"  ✔  {e['nombre_espanol']}: {', '.join(candidatos)}")
            subidos += 1
        else:
            print(f"  ✘  {e['nombre_espanol']}: {resp.status_code} {resp.text[:120]}")
            errores += 1

    print(f"\nListo: {subidos} actualizados, {sin_nada} sin archivos, {errores} con error.")

    # Archivos que no coincidieron con ninguna palabra (por si hay un typo en el nombre)
    slugs = {normalizar(e["nombre_espanol"]) for e in elementos}
    huerfanos = [n for n in imagenes if n not in slugs]
    huerfanos += [n for n in audios if n.rsplit("_", 1)[0] not in slugs]
    if huerfanos:
        print("Sin palabra correspondiente:", ", ".join(sorted(huerfanos)))


if __name__ == "__main__":
    main()
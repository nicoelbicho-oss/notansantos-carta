"""
Audita el menu.json actual contra los datos crudos extraídos del sitio viejo.

Reporta:
 - Items presentes en la carta vieja que NO están en menu.json (faltantes)
 - Items en menu.json que NO estaban en la carta vieja (agregados)
 - Items con precio cambiado entre vieja y actual

Tiene en cuenta:
 - Cambios acordados con el dueño (medialunas eliminadas, etc.)
 - Renombramientos (typos corregidos, normalización de capitalización)
 - Que un mismo vino puede tener variantes: por botella en su bodega
   + por copa en "Vino por copa" (es válido tener 2 precios distintos).
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMIDAS_RAW = ROOT / "notansantos-comidas-raw.json"
VINOS_RAW   = ROOT / "notansantos-vinos-raw.json"
MENU_NEW    = ROOT / "src" / "data" / "menu.json"

# ====== Cambios intencionales ======
QUITADOS = {"medialunas calentitas"}

# Renombramientos vieja → nueva (todos en formato normalizado)
RENOMBRADOS = {
    "fucciles al fierrito": "fusilli al fierrito",      # corrección typo
    "1/4 pollo": "1/4 pollo",                            # ¼ vs 1/4 — norm() los iguala
    "panqueque dulce de leche": "panqueque de dulce de leche",
    "d.v. catena chardonnay - chardonnay": "d.v. catena chardonnay",  # quitado duplicado
    "ns blend collection mk-cab franc-p. ver": "ns blend collection mk · cab franc · p. verdot",
    "matambre  de ternera a la pizza con guarnicion para compartir":
        "matambre de ternera a la pizza con guarnicion para compartir",
}

# Items que MOVIMOS de un lugar a otro (vieja → nueva tarjeta donde está ahora)
# El script revisa que existan, no en qué tarjeta están exactamente.
MOVIDOS = {
    "costillar para compartir": "Especiales (era Parrilla)",
    # Las "Copa X" pasaron a Vino por Copa
    "copa alamos malbec": "Vino por Copa (era Catena)",
    "copa don nicanor": "Vino por Copa (era Nieto)",
    "copa nieto senetiner": "Vino por Copa (era Nieto)",
    "copa ruca malen capitulo 1 malbec": "Vino por Copa (era Ruca Malen)",
    "copa felinos malbec": "Vino por Copa (era Cobos)",
    "copa nina gold petit verdot": "Vino por Copa (era San Huberto)",
    "copa": "Vino por Copa (era San Huberto / Espumantes)",  # genérica
}


def norm(s) -> str:
    if s is None: return ""
    s = str(s).strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.replace("¼", "1/4").replace("½", "1/2")
    s = re.sub(r"\s+", " ", s)
    return s


def norm_precio(p) -> str:
    if not p: return ""
    return re.sub(r"[^\d]", "", str(p))


# ====== Cargar datos ======
with open(COMIDAS_RAW, encoding="utf-8") as f: comidas_raw = json.load(f)
with open(VINOS_RAW,   encoding="utf-8") as f: vinos_raw = json.load(f)
with open(MENU_NEW,    encoding="utf-8") as f: menu_new = json.load(f)


def aplanar_viejos():
    out = []
    for cat in comidas_raw["extracted"]:
        for item in cat["items"]:
            precios = [item["price"]] if item.get("price") else []
            precios += [v["price"] for v in item.get("variants", [])]
            out.append((cat["category"], item["name"], precios))
    for cat in vinos_raw:
        for item in cat["items"]:
            precios = [item["price"]] if item.get("price") else []
            precios += [v["price"] for v in item.get("variants", [])]
            out.append((cat["category"], item["name"], precios))
    return out


def aplanar_nuevos():
    """Devuelve list[(seccion, nombre, precios)] — puede haber duplicados si
    un item aparece en varias secciones (ej. mismo vino en bodega y en Vino por copa)."""
    out = []
    for sec in menu_new["comidas"]:
        for item in sec["items"]:
            precios = [item["precio"]] if item.get("precio") else []
            precios += [v["precio"] for v in item.get("variantes", [])]
            out.append((sec["nombre"], item["nombre"], precios))
        if "submenu" in sec:
            for item in sec["submenu"]["items"]:
                precios = [item["precio"]] if item.get("precio") else []
                precios += [v["precio"] for v in item.get("variantes", [])]
                out.append((sec["nombre"], item["nombre"], precios))
    for t in menu_new["vinos_y_tragos"]["tarjetas"]:
        for g in t["grupos"]:
            for item in g["items"]:
                precios = [item["precio"]] if item.get("precio") else []
                precios += [v["precio"] for v in item.get("variantes", [])]
                out.append((t["nombre"], item["nombre"], precios))
    return out


viejos = aplanar_viejos()
nuevos = aplanar_nuevos()

# Index nuevos por nombre normalizado → lista de ocurrencias
nuevos_idx: dict[str, list] = {}
for sec, nombre, precios in nuevos:
    nuevos_idx.setdefault(norm(nombre), []).append((sec, nombre, precios))


def buscar_en_nuevos(nv: str):
    """Busca un nombre normalizado en el index nuevo. Aplica renombrados si hace falta."""
    if nv in nuevos_idx: return nuevos_idx[nv]
    renombrado = norm(RENOMBRADOS.get(nv, nv))
    if renombrado in nuevos_idx: return nuevos_idx[renombrado]
    # ¿Es una "Copa X" que ahora vive en Vino por copa con otro nombre?
    if nv.startswith("copa "):
        sin = nv[5:]
        if sin in nuevos_idx: return nuevos_idx[sin]
    return None


# ====== REPORTE ======
print("=" * 76)
print("AUDITORÍA DEL menu.json vs CARTA VIEJA")
print("=" * 76)
print(f"\nITEMS EN LA CARTA VIEJA: {len(viejos)}")
print(f"ITEMS EN menu.json:      {len(nuevos)} (entradas en la fuente — puede contar duplicados)")

# 1. Faltantes (vieja → no encontrados en nueva)
faltantes = []
movidos_ok = []
for cat, nombre, precios in viejos:
    nv = norm(nombre)
    if nv in QUITADOS: continue
    if buscar_en_nuevos(nv) is not None:
        if nv in MOVIDOS:
            movidos_ok.append((cat, nombre, MOVIDOS[nv]))
        continue
    faltantes.append((cat, nombre, precios))

print("\n" + "─" * 76)
print(f"1. FALTANTES (carta vieja → no están en menu.json)")
print("─" * 76)
if faltantes:
    for cat, nombre, precios in faltantes:
        print(f"  [!] {cat[:25]:25s} | {nombre:50s} | {precios}")
    print(f"\n  TOTAL FALTANTES: {len(faltantes)}")
else:
    print("  ✓ Todos los ítems están presentes (excepto los quitados intencionalmente).")

if movidos_ok:
    print(f"\n  Movidos intencionalmente (presentes, en otra sección):")
    for cat, nombre, donde in movidos_ok:
        print(f"      {nombre:50s} → {donde}")

# 2. Agregados (nueva → no estaban en vieja)
viejos_keys = set()
for cat, nombre, _ in viejos:
    nv = norm(nombre)
    viejos_keys.add(nv)
    if nv in RENOMBRADOS:
        viejos_keys.add(norm(RENOMBRADOS[nv]))
    if nv.startswith("copa "):
        viejos_keys.add(nv[5:])

agregados = []
for sec, nombre, _ in nuevos:
    nn = norm(nombre)
    if nn in viejos_keys: continue
    if any(norm(RENOMBRADOS.get(vk, vk)) == nn for vk in viejos_keys): continue
    agregados.append((sec, nombre))

print("\n" + "─" * 76)
print(f"2. AGREGADOS (menu.json tiene cosas que no estaban en la vieja)")
print("─" * 76)
if agregados:
    for sec, nombre in agregados:
        print(f"  [+] {sec[:25]:25s} | {nombre}")
    print(f"\n  TOTAL AGREGADOS: {len(agregados)}")
else:
    print("  ✓ No hay ítems agregados.")

# 3. Precios distintos
# Para items que aparecen 1 sola vez en cada lado, comparar.
# Si aparecen varias veces (vino con botella + por copa), no marcar como cambio.
precios_distintos = []
for cat, nombre, precios_viejos in viejos:
    nv = norm(nombre)
    if nv in QUITADOS: continue
    matches = buscar_en_nuevos(nv)
    if not matches: continue
    # Comparar precios contra TODOS los matches: si alguno coincide, no es cambio.
    set_viejo = {norm_precio(p) for p in precios_viejos if p}
    if not set_viejo: continue
    coincide = False
    for _, _, precios_nuevos in matches:
        set_nuevo = {norm_precio(p) for p in precios_nuevos if p}
        # Si todos los precios viejos están en el nuevo (o viceversa), está OK
        if set_viejo == set_nuevo: coincide = True; break
        if set_viejo.issubset(set_nuevo) or set_nuevo.issubset(set_viejo):
            coincide = True; break
    if not coincide:
        precios_distintos.append((cat, nombre, sorted(set_viejo),
                                  [(s, sorted(norm_precio(p) for p in pp if p)) for s, _, pp in matches]))

print("\n" + "─" * 76)
print(f"3. PRECIOS DISTINTOS (cambió el precio entre vieja y nueva)")
print("─" * 76)
if precios_distintos:
    for cat, nombre, pv, pn in precios_distintos:
        print(f"  [$] {nombre} (estaba en {cat})")
        print(f"      vieja: ${pv[0] if pv else '?'}")
        for sec, precios in pn:
            print(f"      nueva ({sec}): {['$'+p for p in precios]}")
        print()
    print(f"  TOTAL CON PRECIO DISTINTO: {len(precios_distintos)}")
else:
    print("  ✓ Todos los precios coinciden.")

print("\n" + "=" * 76)

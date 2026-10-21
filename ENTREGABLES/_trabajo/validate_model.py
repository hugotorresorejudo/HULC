#!/usr/bin/env python3
"""Validación estructural de un .ctehexml del Grupo 9 (no sustituye a abrirlo en HULC).

Comprueba: XML bien formado, codificación/CRLF, IDs únicos, referencias (NEXT-TO,
POLYGON, CONSTRUCTION, LAYERS, GAP, GLASS-TYPE), polígonos cerrados/antihorarios,
áreas > 0, huecos dentro de su muro, y resume áreas por elemento.
Uso: python3 validate_model.py <fichero.ctehexml>
"""
import math
import re
import sys
from lxml import etree


def parse_objects(egl):
    """Devuelve lista de (nombre, tipo, dict de campos) respetando orden."""
    objs = []
    cur = None
    for line in egl.split('\n'):
        m = re.match(r'^\s*"([^"]+)"\s*=\s*([A-Z][A-Z0-9\-]*)\s*$', line)
        if m:
            cur = [m.group(1), m.group(2), {}, []]
            objs.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r'^\s*([A-Za-z_/\-0-9]+)\s*=\s*(.*?)\s*$', line)
        if m:
            cur[2][m.group(1)] = m.group(2)
            cur[3].append((m.group(1), m.group(2)))
    return objs


def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def unq(s):
    return s.strip().strip('"').strip()


def main(path):
    raw = open(path, 'rb').read()
    errs, warns = [], []
    text = raw.decode('utf-8')
    if raw.count(b'\r\n') != raw.count(b'\n'):
        errs.append('Hay finales de línea que no son CRLF')
    root = etree.fromstring(raw)
    egl = root.find('EntradaGraficaLIDER').text.replace('\r\n', '\n')
    objs = parse_objects(egl)
    byname = {}
    for nm, ty, f, _ in objs:
        byname.setdefault((ty, nm), []).append(f)
    # --- IDs únicos para objetos geométricos
    geo_types = {'FLOOR', 'SPACE', 'EXTERIOR-WALL', 'INTERIOR-WALL', 'UNDERGROUND-WALL', 'ROOF', 'WINDOW', 'POLYGON'}
    seen = {}
    for nm, ty, f, _ in objs:
        if ty in geo_types:
            if nm in seen:
                errs.append('ID duplicado: %s (%s y %s)' % (nm, seen[nm], ty))
            seen[nm] = ty
    # --- polígonos
    polys = {}
    for nm, ty, f, kv in objs:
        if ty == 'POLYGON':
            pts = []
            for k, v in kv:
                m = re.match(r'V(\d+)$', k)
                if m:
                    xs = re.findall(r'-?[0-9.eE+\-]+', v)
                    pts.append((float(xs[0]), float(xs[1])))
            polys[nm] = pts
            if len(pts) < 3:
                errs.append('Polígono con <3 vértices: ' + nm)
                continue
            if pts[0] == pts[-1]:
                errs.append('Polígono con primer vértice repetido (debe ir sin cerrar): ' + nm)
            a = area(pts)
            if a <= 0:
                errs.append('Polígono no antihorario o área <= 0: %s (%.4f)' % (nm, a))
    # --- referencias
    layers = {nm for (ty, nm) in byname if ty == 'LAYERS'}
    consts = {nm for (ty, nm) in byname if ty == 'CONSTRUCTION'}
    gaps = {nm for (ty, nm) in byname if ty == 'GAP'}
    glasses = {nm for (ty, nm) in byname if ty == 'GLASS-TYPE'}
    spaces = {nm for (ty, nm) in byname if ty == 'SPACE'}
    sconds = {nm for (ty, nm) in byname if ty == 'SPACE-CONDITIONS'}
    yconds = {nm for (ty, nm) in byname if ty == 'SYSTEM-CONDITIONS'}
    summary = {'wall': {}, 'win': {}, 'roof': 0.0, 'floor_space': {}}
    cur_space = None
    cur_wall = None
    for nm, ty, f, _ in objs:
        if ty == 'SPACE':
            cur_space = nm
            if unq(f['POLYGON']) not in polys:
                errs.append('SPACE %s: polígono inexistente %s' % (nm, f['POLYGON']))
            else:
                summary['floor_space'][nm] = area(polys[unq(f['POLYGON'])])
            if unq(f['SPACE-CONDITIONS']) not in sconds:
                errs.append('SPACE %s: SPACE-CONDITIONS inexistente' % nm)
            if unq(f['SYSTEM-CONDITIONS']) not in yconds:
                errs.append('SPACE %s: SYSTEM-CONDITIONS inexistente' % nm)
        elif ty in ('EXTERIOR-WALL', 'INTERIOR-WALL', 'UNDERGROUND-WALL', 'ROOF'):
            cur_wall = (nm, ty, f)
            c = unq(f.get('CONSTRUCTION', ''))
            if c not in consts:
                errs.append('%s %s: CONSTRUCTION sin definir (%s)' % (ty, nm, c))
            if 'NEXT-TO' in f and unq(f['NEXT-TO']) not in spaces:
                errs.append('%s %s: NEXT-TO inexistente (%s)' % (ty, nm, f['NEXT-TO']))
            if 'POLYGON' in f:
                p = unq(f['POLYGON'])
                if p not in polys:
                    errs.append('%s %s: polígono inexistente %s' % (ty, nm, p))
                elif ty == 'ROOF':
                    summary['roof'] += area(polys[p])
        elif ty == 'CONSTRUCTION':
            ln = unq(f.get('LAYERS', ''))
            if ln and ln not in layers:
                errs.append('CONSTRUCTION %s: LAYERS inexistente %s' % (nm, ln))
        elif ty == 'WINDOW':
            w, h = float(f['WIDTH']), float(f['HEIGHT'])
            if w * h <= 0:
                errs.append('Hueco con área <= 0: ' + nm)
            if unq(f['GAP']) not in gaps:
                errs.append('WINDOW %s: GAP inexistente' % nm)
            if unq(f['GLASS-TYPE']) not in glasses:
                errs.append('WINDOW %s: GLASS-TYPE inexistente' % nm)
            summary['win'][nm] = (w * h, cur_wall[0] if cur_wall else None)
    # floors / planes
    for nm, ty, f, _ in objs:
        if ty == 'FLOOR':
            if unq(f['POLYGON']) not in polys:
                errs.append('FLOOR %s: polígono inexistente' % nm)
            prev = unq(f['PREVIOUS'])
            if prev != 'Ninguna' and ('FLOOR', prev) not in byname:
                errs.append('FLOOR %s: PREVIOUS inexistente %s' % (nm, prev))
    # sistemas: zonas existentes
    for z in root.iter('zona'):
        if unq(z.text) not in spaces:
            errs.append('Sistema: zona inexistente ' + z.text)
    # DatosGenerales coherente
    dg = root.find('DatosGenerales')
    for tag in ('tipoVivienda', 'comunidad', 'zonaClimatica', 'altitud', 'tipoUso', 'valorImpulsionAire',
                'superficieConstruida'):
        print('  DatosGenerales/%s = %s' % (tag, dg.findtext(tag)))
    # --- resumen
    print('Objetos:', len(objs), ' ventanas/puertas:', len(summary['win']))
    for sp, a in summary['floor_space'].items():
        print('  espacio %s área en planta %.3f m2' % (sp, a))
    print('  área total huecos %.3f m2 ; faldones+hastiales (triángulos) %.3f m2' %
          (sum(a for a, _ in summary['win'].values()), summary['roof']))
    for e in errs:
        print('ERROR:', e)
    for w in warns:
        print('AVISO:', w)
    print('RESULTADO:', 'OK' if not errs else '%d errores' % len(errs))
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

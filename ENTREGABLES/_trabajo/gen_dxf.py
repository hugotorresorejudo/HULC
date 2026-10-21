#!/usr/bin/env python3
"""Genera 'Geometria Grupo 9.dxf' (unidades: metros) y una previsualización PNG.

Capas (una por planta, un contorno cerrado por espacio, vértices antihorarios):
  P01 forjado sanitario 9,0 x 7,0 | P02 planta baja (E01 acondicionada, E02 no acondicionada)
  P03 bajocubierta (huella con vértices intermedios en la cumbrera y en la división x=7,5).
Origen (0,0) en la esquina inferior izquierda, X hacia la derecha, Y hacia arriba.
Fuente: Plano CAD.dxf del enunciado (se revisó; solo se corrigen unidades y entidades/capas sobrantes).
"""
import sys
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LX, LY, XD = 9.0, 7.0, 7.5
out_dxf, out_png = sys.argv[1], sys.argv[2]

doc = ezdxf.new('R2018', setup=False)
doc.units = 6  # metros
doc.header['$INSUNITS'] = 6
doc.header['$MEASUREMENT'] = 1
for name, color in (('P01', 1), ('P02', 3), ('P03', 5)):
    doc.layers.add(name, color=color)
msp = doc.modelspace()
shapes = {
    'P01': [[(0, 0), (LX, 0), (LX, LY), (0, LY)]],
    'P02': [[(0, 0), (XD, 0), (XD, LY), (0, LY)], [(XD, 0), (LX, 0), (LX, LY), (XD, LY)]],
    'P03': [[(0, 0), (XD, 0), (LX, 0), (LX, LY / 2), (LX, LY), (XD, LY), (0, LY), (0, LY / 2)]],
}
for layer, polys in shapes.items():
    for pts in polys:
        msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': layer})
doc.saveas(out_dxf)

# ---- comprobación de lectura y de áreas
d2 = ezdxf.readfile(out_dxf)
from ezdxf import recover  # noqa: F401
tot = {}
for e in d2.modelspace():
    pts = [(p[0], p[1]) for p in e.get_points()]
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2
    assert e.closed and a > 0, (e.dxf.layer, a)
    tot[e.dxf.layer] = tot.get(e.dxf.layer, 0) + a
print('Áreas por capa (m2):', tot)

# ---- PNG
fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
titles = {'P01': 'P01 · Forjado sanitario (no habitable)', 'P02': 'P02 · Planta baja (2 zonas)', 'P03': 'P03 · Bajocubierta (no habitable)'}
cols = {'P01': '#c9c9c9', 'P02': ['#9ecae1', '#fdd0a2'], 'P03': '#c7e9c0'}
for ax, (layer, polys) in zip(axs, shapes.items()):
    for k, pts in enumerate(polys):
        c = cols[layer][k] if layer == 'P02' else cols[layer]
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]
        ax.fill(xs, ys, color=c, ec='k', lw=1.4)
        for x, y in pts:
            ax.plot(x, y, 'ko', ms=3)
    ax.set_aspect('equal')
    ax.set_xlim(-0.8, LX + 0.8)
    ax.set_ylim(-0.8, LY + 0.8)
    ax.set_title(titles[layer], fontsize=9)
    ax.set_xlabel('x [m]')
    ax.grid(alpha=.3)
axs[0].set_ylabel('y [m]')
axs[1].text(XD / 2, LY / 2, 'E01\nacondicionada\n52,5 m²', ha='center', va='center', fontsize=8)
axs[1].text((XD + LX) / 2, LY / 2, 'E02\nno acond.\n10,5 m²', ha='center', va='center', fontsize=7)
axs[2].plot([0, LX], [LY / 2, LY / 2], 'r--', lw=1)
axs[2].text(LX / 2, LY / 2 + 0.2, 'cumbrera (paralela a X)', color='r', ha='center', fontsize=8)
fig.suptitle('Grupo 9 · Geometría para HULC (orientación 315°: F1 = suroeste)', fontsize=10)
fig.tight_layout()
fig.savefig(out_png, dpi=170)
print('OK')

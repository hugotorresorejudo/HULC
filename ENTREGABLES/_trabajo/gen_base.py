#!/usr/bin/env python3
"""Genera 'Modelo Base CTE.ctehexml' del Grupo 9 a partir de las plantillas de clase.

Plantilla geometría/biblioteca : sesion_1_natalia_v2.ctehexml (vivienda unifamiliar)
Plantilla condición no acond.  : sesion_1_natalia_v3.ctehexml (bloques Res-No_acondicionado)
Plantilla sistemas             : sesion_1_natalia_v3.ctehexml (SIS_Autonomo + SIS_Acs)

Uso: python3 gen_base.py <dir_plantillas> <salida.ctehexml>
Conserva UTF-8 + CRLF + CDATA de la plantilla (edición a nivel de texto).
"""
import math
import re
import sys

# ----------------------------------------------------------------- datos Grupo 9
LX, LY = 9.0, 7.0
XDIV = 7.5               # zona acondicionada 0..7.5, no acondicionada 7.5..9
H_PB = 2.5               # altura de planta
H_FS = 0.85              # forjado sanitario
H_BC = 1.2               # alero -> cumbrera
Z_P01 = -0.7
Z_P02 = 0.15
Z_P03 = Z_P02 + H_PB     # 2.65
AZIMUT = 315.0
VENT_LS = 33.0           # caudal HS3 (l/s)
VENT_M3H = VENT_LS * 3.6
ACS_LDIA = 4 * 28 * 0.9  # 100,8 l/dia
WIN_W = WIN_H = 1.2
SILL = 0.9
DOOR_W, DOOR_H = 0.9, 2.1
PROJECT = "Grupo9_CasoBase_Madrid"

SLOPE_LEN = math.hypot(LY / 2, H_BC)                 # 3.7
TILT = math.degrees(math.atan2(H_BC, LY / 2))        # 18.92


def n(v, w=14):
    """Formato numerico estilo LIDER (ancho fijo, sin ceros sobrantes)."""
    s = ('%.6f' % v).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s.rjust(w)


def frame_width(w, h, frac=0.15):
    # (w-2a)(h-2a) = (1-frac) w h
    A, B, C = 4.0, -2.0 * (w + h), frac * w * h
    return (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)


# ----------------------------------------------------------------- plantillas
def read(path):
    return open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def egl_of(raw):
    i = raw.index('<![CDATA[') + len('<![CDATA[')
    j = raw.index(']]>', i)
    return i, j


def build_geometry(tpl_egl):
    """Devuelve el texto LIDER completo del Grupo 9."""
    t = tpl_egl
    # --- cortes
    m_aux = t.index('$ -----------------\n$ Lineas Auxiliares')
    m_geo = t.index('$\n$ +-------------------+\n$ | DATOS GEOM')
    m_floor = t.index('"P01" = FLOOR')
    m_cond = t.index('$\n$ +---------------------------+\n$ | CONDICIONES OPERACIONALES')
    pre = t[:m_aux]
    geo_block = t[m_geo:m_floor]            # Run period + BUILD-PARAMETERS
    post = t[m_cond:]

    # ---- lineas auxiliares y planos y poligonos
    z_ridge = Z_P03 + H_BC
    out = [pre]
    out.append('$ -----------------\n$ Lineas Auxiliares\n$ -----------------\n$\n')
    out.append('"Linea1" = AUX-LINE\n           TYPE = 1\n'
               '           X0   = 0.000000\n           Y0   = %.6f\n           Z0   = %.6f\n'
               '           X1   = %.6f\n           Y1   = %.6f\n           Z1   = %.6f\n'
               '           OWNERF = "P03"\n           OWNERS = "(null)"\n           ..\n'
               % (LY / 2, z_ridge, LX, LY / 2, z_ridge))
    out.append('$ ------\n$ Planos\n$ ------\n$\n')
    for k, (pn, layer) in enumerate([('Plano001', 'P01'), ('Plano002', 'P02'), ('Plano003', 'P03')]):
        out.append('"%s" = PLANE \n    PLANE_TYPE = DXF\n    FILE = "Geometria Grupo 9.dxf"\n'
                   '    UNIT = 1.000000\n    X    = 0.000000\n    Y    = 0.000000\n    Z    = 0.000000\n'
                   '    ACADLAYER = ("%s")\n      ..\n' % (pn, layer))
    out.append('\n$ ---------\n$ POLIGONOS\n$ ---------\n$\n')

    def poly(name, pts):
        s = '"%s" = POLYGON\n' % name
        for i, (x, y) in enumerate(pts, 1):
            s += '    V%d   =( %s, %s )\n' % (i, ('%g' % x), ('%g' % y))
        return s + '    ..\n'

    unit = [(0, 0), (1, 0), (1, 1), (0, 1)]
    e01 = [(0, 0), (XDIV, 0), (XDIV, LY), (0, LY)]
    e02 = [(XDIV, 0), (LX, 0), (LX, LY), (XDIV, LY)]
    full = [(0, 0), (LX, 0), (LX, LY), (0, LY)]
    attic = [(0, 0), (XDIV, 0), (LX, 0), (LX, LY / 2), (LX, LY), (XDIV, LY), (0, LY), (0, LY / 2)]
    out.append(poly('P01_Poligono1', unit))
    out.append(poly('P01_E01_Poligono2', full))
    out.append(poly('P02_Poligono1', unit))
    out.append(poly('P02_E01_Poligono2', e01))
    out.append(poly('P02_E02_Poligono3', e02))
    out.append(poly('P03_Poligono1', unit))
    out.append(poly('P03_E01_Poligono2', attic))
    # polígonos locales de los suelos del bajocubierta (X=zona, Y=LY) -> ver FI001/FI002
    out.append(poly('P03_E01_FI001_Poligono3', [(0, 0), (LY, 0), (LY, XDIV), (0, XDIV)]))
    out.append(poly('P03_E01_FI002_Poligono4', [(0, 0), (LY, 0), (LY, LX - XDIV), (0, LX - XDIV)]))
    # faldones (2 triangulos por cara) y hastiales (1 triangulo)
    L = SLOPE_LEN
    tri_a = lambda w: [(0, 0), (0, -L), (w, -L)]
    tri_b = lambda w: [(0, 0), (w, -L), (w, 0)]
    out.append(poly('P03_E01C001_Poligono5', tri_a(LX)))
    out.append(poly('P03_E01C002_Poligono6', tri_b(LX)))
    out.append(poly('P03_E01C003_Poligono7', tri_a(LX)))
    out.append(poly('P03_E01C004_Poligono8', tri_b(LX)))
    out.append(poly('P03_E01C005_Poligono9', [(0, 0), (-LY / 2, -H_BC), (LY / 2, -H_BC)]))
    out.append(poly('P03_E01C006_Poligono10', [(0, 0), (-LY / 2, -H_BC), (LY / 2, -H_BC)]))
    out.append(geo_block)

    # ---- plantas y espacios
    construction = lambda cname, lname, extra='': (
        '                  "%s" =  CONSTRUCTION\n                        TYPE   = LAYERS  \n'
        '                        LAYERS = "%s" \n%s                        ..\n' % (cname, lname, extra))
    FAC = ('F 1.0130.60', 'F 1.013', '                        ABSORPTANCE = 0.600000\n')

    def space_head(name, height, poly_name, typ, cond):
        return ('    "%s" = SPACE\n        nCompleto = "%s"\n              HEIGHT        = %s\n'
                '            SHAPE             = POLYGON \n            POLYGON           = "%s"\n'
                '            TYPE              = %s\n            SPACE-TYPE        = "Residencial"\n'
                '            SYSTEM-CONDITIONS = "%s"\n            SPACE-CONDITIONS  = "%s"\n'
                '            FLOOR-WEIGHT      =              0\n            MULTIPLIER        = 1\n'
                '            MULTIPLIED        = 0\n            PILLARS-NUMBERS   = 0\n'
                '       FactorSuperficieUtil   = 1.0\n       perteneceALaEnvolventeTermica   = SI\n'
                '           INTERIOR-RADIATION  = FIXED\n           POWER     = 4.4\n'
                '           VEEI-OBJ  = 7.000000\n           VEEI-REF  = 10.000000\n            ..\n'
                % (name, name, n(height), poly_name, typ, cond, cond))

    def floor_head(name, z, h, prev):
        return ('"%s" = FLOOR\n      Z             = %s\n      POLYGON       =  "%s_Poligono1"\n'
                '      FLOOR-HEIGHT  = %s\n      SPACE-HEIGHT  = %s\n      SHAPE         =  POLYGON\n'
                '      PREVIOUS      =  "%s"\n      ..\n' % (name, n(z), name, n(h), n(h), prev))

    def window(wall, idx, x, y, w, h, door):
        nm = '%s_V' % wall if idx == 0 else '%s_V_%d' % (wall, idx)
        if door:
            fw, gap, glass, tj, cond, inf = DOOR_W / 2, 'Puerta', 'HOR_DB1_4-12-331', '0.680000', '2', 60
        else:
            fw, gap, glass, tj, cond, inf = frame_width(w, h), 'Ventana_clase', 'VER_DB2_4-15-6', '0.080000', '4.324', 27
        return ('                  "%s" = WINDOW\n                        X              = %s\n'
                '                        Y              = %s\n                        SETBACK        =              0\n'
                '                        HEIGHT         = %s\n                        WIDTH          = %s\n'
                '                        GAP            = "%s"\n'
                '                        COEFF = ( 1.000000, 1.000000, 1.000000, 1.000000)\n'
                '            transmisividadJulio        = %s\n            HayConAutDisSomMov         = "300"\n'
                '                        GLASS-TYPE     = "%s"\n                        FRAME-WIDTH   = %s\n'
                '                        FRAME-CONDUCT = %s\n                        FRAME-ABS     =            0.7\n'
                '                        INF-COEF       = %s\n'
                '                        OVERHANG-A     =              0\n                        OVERHANG-B     =              0\n'
                '                        OVERHANG-W     =              0\n                        OVERHANG-D     =              0\n'
                '                        OVERHANG-ANGLE =              0\n                        LEFT-FIN-A     =              0\n'
                '                        LEFT-FIN-B     =              0\n                        LEFT-FIN-H     =              0\n'
                '                        LEFT-FIN-D     =              0\n                        RIGHT-FIN-A    =              0\n'
                '                        RIGHT-FIN-B    =              0\n                        RIGHT-FIN-H    =              0\n'
                '                        RIGHT-FIN-D    =              0\n                        ..\n'
                % (nm, n(x, 14), n(y, 14), n(h, 14), n(w, 14), gap, tj, glass,
                   n(fw, 14), n(float(cond), 14), n(inf, 14)))

    def ext_wall(space, k, loc, wins=()):
        nm = '%s_PE%03d' % (space, k)
        s = ('            "%s" = EXTERIOR-WALL\n                  ABSORPTANCE   =            0.6\n'
             '                  COMPROBAR-REQUISITOS-MINIMOS = YES\n                  TYPE_ABSORPTANCE    = 1\n'
             '                  COLOR_ABSORPTANCE   = 0\n                  DEGREE_ABSORPTANCE   = 2\n'
             '                  CONSTRUCCION_MURO  = "F 1.013"  \n                  CONSTRUCTION  = "F 1.0130.60"  \n'
             '                  LOCATION      = %s  \n                        ..\n' % (nm, loc))
        s += construction(*FAC)
        for i, (x, y, w, h, door) in enumerate(wins):
            s += window(nm, i, x, y, w, h, door)
        return s

    def int_wall(space, nm, nxt, cons, loc_lines):
        return ('            "%s_%s" = INTERIOR-WALL\n                  INT-WALL-TYPE = STANDARD  \n'
                '                  NEXT-TO       = "%s"  \n   COMPROBAR-REQUISITOS-MINIMOS = NO\n'
                '                  CONSTRUCTION  = "%s"  \n%s                        ..\n'
                % (space, nm, nxt, cons, loc_lines)) + construction(cons, cons)

    body = []
    # ---------------- P01 forjado sanitario
    body.append(floor_head('P01', Z_P01, H_FS, 'Ninguna'))
    body.append(space_head('P01_E01', H_FS, 'P01_E01_Poligono2', 'UNHABITED', 'NIVEL_ESTANQUEIDAD_1'))
    body.append('            "P01_E01_FTER001" = UNDERGROUND-WALL\n                  Z-GROUND      =              0\n'
                '   COMPROBAR-REQUISITOS-MINIMOS = YES\n                  CONSTRUCTION  = "MTh6"  \n'
                '                  LOCATION      = BOTTOM  \n                   AREA          = %s\n'
                '                   PERIMETRO     = %s\n                        ..\n' % (n(LX * LY, 14), n(2 * (LX + LY), 14))
                + construction('MTh6', 'MTh6'))
    for k in range(1, 5):
        body.append(('            "P01_E01_PE%03d" = EXTERIOR-WALL\n                  ABSORPTANCE   =            0.6\n'
                     '                  COMPROBAR-REQUISITOS-MINIMOS = YES\n                  TYPE_ABSORPTANCE    = %d\n'
                     '                  COLOR_ABSORPTANCE   = 0\n                  DEGREE_ABSORPTANCE   = 2\n'
                     '                  CONSTRUCCION_MURO  = "F 1.013"  \n                  CONSTRUCTION  = "F 1.0130.60"  \n'
                     '                  Z             =            0.7\n                  LOCATION      = SPACE-V%d  \n'
                     '                   HEIGHT        =           0.15\n                        ..\n') % (k, 1 if k == 3 else 0, k)
                    + construction(*FAC))
        body.append(('            "P01_E01_PCT%03d" = UNDERGROUND-WALL\n                  Z-GROUND      =              0\n'
                     '   COMPROBAR-REQUISITOS-MINIMOS = YES\n                  CONSTRUCTION  = "Muro terreno"  \n'
                     '                  LOCATION      = SPACE-V%d  \n                   HEIGHT        =            0.7\n'
                     '                        ..\n') % (k, k) + construction('Muro terreno', 'Muro terreno'))

    # ---------------- P02 planta baja
    body.append(floor_head('P02', Z_P02, H_PB, 'P01'))
    # E01 acondicionada
    body.append(space_head('P02_E01', H_PB, 'P02_E01_Poligono2', 'CONDITIONED', 'Residencial'))
    body.append(int_wall('P02_E01', 'FI001', 'P01_E01', 'PIH_l7', '                  LOCATION      = BOTTOM  \n'))
    body.append(int_wall('P02_E01', 'Med001', 'P02_E02', 'PIV por defecto4', '                  LOCATION      = SPACE-V2  \n'))
    # F1: ventana, puerta, 2 ventanas (X desde V1 = x=0)
    f1 = [(1.65 - WIN_W / 2, SILL, WIN_W, WIN_H, False),
          (3.75 - DOOR_W / 2, 0.0, DOOR_W, DOOR_H, True),
          (5.025 - WIN_W / 2, SILL, WIN_W, WIN_H, False),
          (6.675 - WIN_W / 2, SILL, WIN_W, WIN_H, False)]
    body.append(ext_wall('P02_E01', 1, 'SPACE-V1', f1))
    # F3 (V3->V4): X desde x=7.5; centrada en el tramo acondicionado
    body.append(ext_wall('P02_E01', 2, 'SPACE-V3', [(XDIV / 2 - WIN_W / 2, SILL, WIN_W, WIN_H, False)]))
    # F4 (V4->V1): X desde y=7
    body.append(ext_wall('P02_E01', 3, 'SPACE-V4', [(LY / 2 - WIN_W / 2, SILL, WIN_W, WIN_H, False)]))
    # E02 no acondicionada
    body.append(space_head('P02_E02', H_PB, 'P02_E02_Poligono3', 'UNCONDITIONED', 'Res-No_acondicionado'))
    body.append(int_wall('P02_E02', 'FI002', 'P01_E01', 'PIH_l7', '                  LOCATION      = BOTTOM  \n'))
    body.append(ext_wall('P02_E02', 1, 'SPACE-V1'))
    body.append(ext_wall('P02_E02', 2, 'SPACE-V2', [(LY / 2 - WIN_W / 2, SILL, WIN_W, WIN_H, False)]))
    body.append(ext_wall('P02_E02', 3, 'SPACE-V3'))

    # ---------------- P03 bajocubierta
    body.append(floor_head('P03', Z_P03, H_BC, 'P02'))
    body.append(space_head('P03_E01', H_BC, 'P03_E01_Poligono2', 'UNHABITED', 'NIVEL_ESTANQUEIDAD_1'))

    def attic_floor(nm, nxt, x0, poly_name):
        return ('            "%s" = INTERIOR-WALL\n                  INT-WALL-TYPE = STANDARD  \n'
                '                  NEXT-TO       = "%s"  \n   COMPROBAR-REQUISITOS-MINIMOS = NO\n'
                '                  CONSTRUCTION  = "PIH_l7"  \n                  X             = %s\n'
                '                  Y             =              0\n                  Z             =              0\n'
                '                  AZIMUTH       =             90\n                  TILT          =            180\n'
                '                  POLYGON       = "%s"\n                        ..\n' % (nm, nxt, n(x0), poly_name)
                + construction('PIH_l7', 'PIH_l7'))
    body.append(attic_floor('P03_E01_FI001', 'P02_E01', 0, 'P03_E01_FI001_Poligono3'))
    body.append(attic_floor('P03_E01_FI002', 'P02_E02', XDIV, 'P03_E01_FI002_Poligono4'))

    def roof(nm, x, y, az, tilt, poly_name, cons, cons_block, tabs):
        return ('            "%s" = ROOF\n                  ABSORPTANCE   =            0.6\n'
                '                  COMPROBAR-REQUISITOS-MINIMOS = YES\n                  TYPE_ABSORPTANCE    = %d\n'
                '                  COLOR_ABSORPTANCE   = 0\n                  DEGREE_ABSORPTANCE   = 2\n'
                '                  CONSTRUCTION  = "%s"  \n                  X             = %s\n'
                '                  Y             = %s\n                  Z             = %s\n'
                '                  AZIMUTH       = %s\n                  TILT          = %s\n'
                '                  POLYGON       = "%s"\n                        ..\n'
                % (nm, tabs, cons, n(x), n(y), n(H_BC), n(az), n(tilt), poly_name)) + cons_block
    qifa = construction('Qifa_ue5', 'Qifa_ue5')
    gab = construction('F 1.013', 'F 1.013')
    body.append(roof('P03_E01C001', 0, LY / 2, 180, TILT, 'P03_E01C001_Poligono5', 'Qifa_ue5', qifa, 1))
    body.append(roof('P03_E01C002', 0, LY / 2, 180, TILT, 'P03_E01C002_Poligono6', 'Qifa_ue5', qifa, 0))
    body.append(roof('P03_E01C003', LX, LY / 2, 0, TILT, 'P03_E01C003_Poligono7', 'Qifa_ue5', qifa, 1))
    body.append(roof('P03_E01C004', LX, LY / 2, 0, TILT, 'P03_E01C004_Poligono8', 'Qifa_ue5', qifa, 0))
    body.append(roof('P03_E01C005', LX, LY / 2, 90, 90, 'P03_E01C005_Poligono9', 'F 1.013', gab, 1))
    body.append(roof('P03_E01C006', 0, LY / 2, 270, 90, 'P03_E01C006_Poligono10', 'F 1.013', gab, 1))

    out.append(''.join(body))

    # ---- condiciones: insertar Res-No_acondicionado y puentes termicos
    out.append(post)
    return ''.join(out)


def patch_conditions_and_pt(egl, v3_egl):
    # bloques Res-No_acondicionado desde v3
    a = v3_egl.index('"Res-No_acondicionado" = SPACE-CONDITIONS')
    b = v3_egl.index('"Residencial" = SPACE-CONDITIONS')
    block = v3_egl[a:b]
    k = egl.index('"Residencial" = SPACE-CONDITIONS')
    egl = egl[:k] + block + egl[k:]
    # longitudes de puentes termicos (estimacion; HULC las recalcula con el boton de calculo)
    per = 2 * (LX + LY)
    win_n = 6
    door = 1
    lengths = {
        'FRENTE_FORJADO': per,
        'UNION_CUBIERTA': per,
        'ESQUINA_CONVEXA': 4 * H_PB,
        'HUECO_CAPIALZADO': win_n * WIN_W + door * DOOR_W,
        'HUECO_JAMBA': win_n * 2 * WIN_H + door * 2 * DOOR_H,
        'HUECO_ALFEIZAR': win_n * WIN_W + door * DOOR_W,
    }
    for name, val in lengths.items():
        pat = re.compile(r'("%s" = THERMAL-BRIDGE\n\s+LONG-MOD-TOTAL = )[-0-9.]+' % name)
        egl, c = pat.subn(lambda m: m.group(1) + '%.6f' % val, egl)
        assert c == 1, name
    return egl


SYSTEMS_XML_ACS_ED = None


def patch_systems(raw_v3, ut_cap_tot, ut_cap_sen, ut_cap_cal, ut_vol):
    i = raw_v3.index('<Definicion_Sistema>')
    j = raw_v3.index('</Definicion_Sistema>') + len('</Definicion_Sistema>')
    s = raw_v3[i:j]
    # ---- unidad exterior Daikin RXC50C
    rep = {
        '<capTotRefNom>12.6000003814697</capTotRefNom>': '<capTotRefNom>5.1</capTotRefNom>',
        '<conRefNom>3.35999989509583</conRefNom>': '<conRefNom>1.55</conRefNom>',
        '<capCalNom>13.8000001907349</capCalNom>\n\t\t\t\t\t\t\t<conCalNom>3.9300000667572</conCalNom>':
            '<capCalNom>5.62</capCalNom>\n\t\t\t\t\t\t\t<conCalNom>1.514</conCalNom>',
    }
    for a, b in rep.items():
        assert a in s, a
        s = s.replace(a, b)
    # ---- unidades interiores: solo 1 en P02_E01
    m0 = s.index('<UT_ED_UnidadInterior nombre="SIS_UT3">')
    m1 = s.index('<UT_ED_UnidadInterior nombre="SIS_UT1">')
    s = s[:m0] + s[m1:]
    ut_a = s.index('<UT_ED_UnidadInterior nombre="SIS_UT1">')
    ut_b = s.index('</UT_ED_UnidadInterior>', ut_a)
    ut = ('<UT_ED_UnidadInterior nombre="SIS_UT1">\n\t\t\t\t\t\t\t<zona>"P02_E01"</zona>\n'
          '\t\t\t\t\t\t\t<nombre_usuario>SIS_UT1_Unidad_interior_de_autnomo</nombre_usuario>\n'
          '\t\t\t\t\t\t\t<capTotRefNom>%s</capTotRefNom>\n\t\t\t\t\t\t\t<capSenRefNom>%s</capSenRefNom>\n'
          '\t\t\t\t\t\t\t<capCalNom>%s</capCalNom>\n\t\t\t\t\t\t\t<vImpulsionNom>%s</vImpulsionNom>\n'
          '\t\t\t\t\t\t\t<vVentilacion>0</vVentilacion>\n\t\t\t\t\t\t\t<dtTermostato>1</dtTermostato>\n'
          '\t\t\t\t\t\t\t<multiplicador>1</multiplicador>\n\t\t\t\t\t\t' % (ut_cap_tot, ut_cap_sen, ut_cap_cal, ut_vol))
    s = s[:ut_a] + ut + s[ut_b:]
    # ---- ACS: Thema Condens 26, demanda 100,8 l/dia
    s = s.replace('<capNom>25.00</capNom>', '<capNom>26.00</capNom>')
    s = s.replace('<conACSDiario>100</conACSDiario>', '<conACSDiario>%.1f</conACSDiario>' % ACS_LDIA)
    # ---- ventilador (bloque terciario no aplica a vivienda)
    k = s.index('<datosVentilacionTerciario>')
    k2 = s.index('</datosVentilacionTerciario>') + len('</datosVentilacionTerciario>')
    s = s[:k].rstrip('\t\n') + '\n\t' + s[k2:].lstrip('\n\t')
    return s


def vent_string():
    p = 126.0 * 0.189   # Qref (m3/h) * SPI -> Q < Qref -> P = Pref
    return ('1;%.3f;%.2f;1;182.00;48.90;0.035;0.189;0;0;0;0;0;0;0;0;0;0;0;0;0;00;0.0000;0.00;%.3f;0.00;0.00;0.0000'
            % (VENT_M3H, p, VENT_M3H)), p


def main(tpl_dir, out_path):
    v2 = read(tpl_dir + '/sesion_1_natalia_v2.ctehexml')
    v3 = read(tpl_dir + '/sesion_1_natalia_v3.ctehexml')
    i, j = egl_of(v2)
    egl2 = v2[i:j]
    i3, j3 = egl_of(v3)
    egl3 = v3[i3:j3]
    egl = build_geometry(egl2)
    egl = patch_conditions_and_pt(egl, egl3)
    # ---- datos generales dentro del EGL
    vs, p_fan = vent_string()
    subs = [
        (r'(BUILDING-AREA\s+= )"[^"]*"', r'\g<1>"%.2f"' % (LX * LY)),
        (r'(TOTAL-HEIGHT\s+= )"[^"]*"', r'\g<1>"%.2f"' % (Z_P03 + H_BC)),
        (r'(FLOORS-ABOVE-GROUND-LEVEL\s+= )\d+', r'\g<1>1'),
        (r'(NAME-PROJECT\s+= \t?)"[^"]*"', r'\g<1>"%s"' % PROJECT),
        (r'(VALORES-VENTILACION = )\( "1.00"', r'\g<1>( "%.2f"' % VENT_LS),
    ]
    for pat, rep in subs:
        egl, c = re.subn(pat, rep, egl, count=1)
        assert c == 1, pat
    # ---- ensamblado
    raw = v2
    head = raw[:i]
    tail = raw[j:]
    # sistemas
    sysxml = patch_systems(v3, '5.1', '3.315', '5.62', '732')
    k = tail.index('<Definicion_Sistema>')
    k2 = tail.index('</Definicion_Sistema>') + len('</Definicion_Sistema>')
    tail = tail[:k] + sysxml + tail[k2:]
    out = head + egl + tail

    def setx(tag, val):
        nonlocal out
        pat = re.compile(r'(<%s>)[^<]*(</%s>)' % (tag, tag))
        out, c = pat.subn(lambda m: m.group(1) + val + m.group(2), out, count=1)
        assert c == 1, tag
    setx('nomPro', PROJECT)
    setx('superficieConstruida', '%.2f' % (LX * LY))
    setx('SupConsCubierta', '%.2f' % (LX * LY))
    setx('alturaTotal', '%.2f' % (Z_P03 + H_BC))
    setx('plantaSobreRasante', '1')
    setx('valorImpulsionAire', '%.2f' % VENT_LS)
    setx('datosVentilacion', vs)
    setx('venPotEC', '%.3f' % p_fan)
    open(out_path, 'wb').write(out.replace('\n', '\r\n').encode('utf-8'))
    print('OK ->', out_path, len(out))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

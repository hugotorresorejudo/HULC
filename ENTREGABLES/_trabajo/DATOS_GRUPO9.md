# DATOS DEL GRUPO 9 (con fuente)

Abreviaturas: **GEO** = Geometrias_asignadas_Trabajo_HULC_Grupos_01_24_2026_v3_revDNS.pdf; **ENU** = Instrucciones_Trabajo_HULC_en_Grupo_2026.pdf; **VENT** = Ventilacion y ACS viviendas.xlsx (dentro de «Catálogos y recursos adicionales…zip»); **MAN** = ManualDeUsuarioHULC.pdf (DB-HE 2019, v0.1, jul 2024); **PV** = Ayuda dimensionamiento Instalación PV_v2.pdf; **CAD** = ENTREGABLES/Plano CAD.dxf.

## 1. Geometría y uso (GEO p. 5, «Grupo 09»)
| Dato | Valor | Fuente |
|---|---|---|
| Uso | Vivienda unifamiliar | GEO p. 5 |
| Nº de plantas | 1 | GEO p. 5 |
| Dimensiones exteriores Lx × Ly | 9,0 × 7,0 m (huella 63,0 m²) | GEO p. 5 |
| Altura de planta | 2,50 m | GEO p. 5 |
| Programa | 3 dormitorios, salón-comedor, cocina y 2 baños | GEO p. 5 |
| Zona acondicionada | 0,00 ≤ x ≤ 7,50 m, 0 ≤ y ≤ 7,00 m (52,5 m²) | GEO p. 5 |
| Zona no acondicionada | 7,50 ≤ x ≤ 9,00 m, 0 ≤ y ≤ 7,00 m (10,5 m²) | GEO p. 5 |
| Orientación | 315° → F1 suroeste, F2 sureste, F3 noreste, F4 noroeste | GEO p. 5 y tabla p. 2 |
| Puerta | En F1, tramo de la zona acondicionada, 0,90 × 2,10 m, centrada en el tramo | GEO p. 5 y p. 1 |
| Ventanas | 6: 3 en F1, 1 en F2, 1 en F3, 1 en F4; vivienda 1,20 × 1,20 m, antepecho 0,90 m, centradas y repartidas uniformemente por tramo | GEO p. 5 y p. 2 |
| Cubierta | Dos aguas, cumbrera centrada paralela al eje X, 1,20 m de alero a cumbrera (pendiente = atan(1,2/3,5) ≈ 18,9°) | GEO p. 5 y p. 2 |
| Forjado sanitario | 0,85 m, un único espacio NO habitable con la misma huella | GEO p. 1; ENU p. 1 |
| Bajocubierta | Espacio NO habitable con la misma huella | GEO p. 1; ENU p. 1 |
| Origen y fachadas | (0,0) esquina inferior izquierda; F1 y=0, F2 x=Lx, F3 y=Ly, F4 x=0 | GEO p. 1 |
| Localidad inicial | Madrid | GEO p. 2; ENU p. 1 |

## 2. Datos climáticos del modelo base
| Dato | Valor | Fuente |
|---|---|---|
| Localidad / zona / altitud | Madrid, D3, 780 m | Plantillas de clase `sesion_1_natalia_v2.ctehexml` (DatosGenerales) — coherentes con el encargo; Anejo B no incluido en la documentación |
| Ventilación | **33 l/s** (caudal HS3 para 3 dormitorios) = 118,8 m³/h. **No es un 33 %**: el «33» del encargo es un caudal en l/s | VENT, hoja «Ventilación», fila 3 dormitorios (D10 = 33 l/s; E10 = D10·3,6); MAN p. 29 (ejemplo 16 × 33 l/s) |
| Ocupación de cálculo | 4 personas (3 dormitorios) | VENT, hoja «ACS», D10 |
| Demanda ACS | 4 pers × 28 l/pers·día × FC 0,9 = **100,8 l/día** | VENT, hoja «ACS», F5 = 28, F10 = 0,9, G10 |
| Ventilador de ventilación | Siber Silentium HIR3V (curva: 50,4 m³/h–22 W; 86,4–23; 118,8–24; 122,4–24) | VENT, hojas «Ventilación»/«ACS» filas 25-30; ficha «Modelo Siber Silentium HIR3V.pdf» |

## 3. Sistemas iniciales propuestos en la documentación
| Servicio | Equipo de la práctica | Fuente |
|---|---|---|
| Calefacción + ACS | Caldera de condensación Saunier Duval Thema Condens 26/31 (η ErP 94 %, 106,2–107 % PCI a 50/30 °C, 98 % a 80/60) | `FT caldera condensación 2021262.pdf` |
| Refrigeración (y calefacción alternativa) | Split Daikin Sensira FTXC-C (SEER/SCOP en el catálogo) | `Catálogo Daikin FTXC-C Sensira.pdf` |
| Ventilación | VMC higrorregulable Siber Silentium HIR3V; ficha ErP Siber VMC AMC 3V (sin recuperación, SPI 0,189 W/(m³/h)) | fichas Siber |
| FV | Procedimiento PVGIS, módulo tipo 54 celdas 420–460 W, ≈1,95 m², pérdidas ≈14 %, azimut 0° = Sur | PV pp. 1-4 |

## 4. Datos NO disponibles en la documentación (ver PLAN_DE_TRABAJO.md, supuestos)
- Límites normativos DB-HE (K, U máx., qsol;jul, n50, Cep,nren, Cep,tot) y factores de paso: **no están en la documentación**; MAN (cap. 6, 10) solo describe los indicadores sin valores.
- Valores ψ por defecto de los puentes térmicos (están solo en la Figura 60 del MAN).
- Posición exacta de las ventanas en F1 (la puerta centrada y 3 ventanas «uniformemente repartidas» en el mismo tramo es ambiguo) y tramo de F3 (cruza ambas zonas).
- Datos del grupo (nombres de integrantes): no suministrados.

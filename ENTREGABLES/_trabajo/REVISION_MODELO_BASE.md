# REVISIÓN / CONSTRUCCIÓN DEL MODELO BASE (Grupo 9)

**Situación:** no existía ningún .ctehexml base (`Modelo Base CTE.dwg` es un dibujo CAD). Por decisión del usuario, `Modelo Base CTE.ctehexml` se **construye desde cero** con `gen_base.py` a partir de las plantillas de clase (`sesion_1_natalia_v2` para geometría y biblioteca, `sesion_1_natalia_v3` para condiciones «no acondicionado» y sistemas). Se conserva UTF-8, CRLF, CDATA y el orden de la plantilla. El original DWG está copiado en `_original/`.

| Dato | Plantilla | Valor del Grupo 9 aplicado | Fuente |
|---|---|---|---|
| Geometría | 6,5×5 m, 2 plantas habitables, bajocubierta acondicionado | 9,0×7,0 m, 1 planta, P01 forjado (UNHABITED), P02 con E01 acondicionada (0–7,5) y E02 no acondicionada (7,5–9), P03 bajocubierta (UNHABITED) | GEO p. 5, p. 1 |
| Alturas | 2,5 / 3,0 m | P01 0,85 · P02 2,50 · P03 1,20 (cumbrera abs. 3,85 m) | GEO p. 5 |
| Cubierta | cumbrera paralela a Y | cumbrera paralela a X en y = 3,5; 2 faldones (inclinación 18,92°, 3,70 m) + 2 hastiales con fachada | GEO p. 5 |
| Orientación | 315° | 315° (sin cambio) | GEO p. 5 |
| Huecos | 2 ventanas + puerta | Puerta 0,90×2,10 y 3 ventanas en F1 (zona acond.), 1 en F2 (zona no acond.), 1 en F3, 1 en F4; 1,20×1,20, antepecho 0,90 | GEO p. 5, p. 2; supuestos S1/S2 |
| Ventilación | 1 l/s | 33 l/s (118,8 m³/h); ventilador ficha ErP Siber VMC AMC 3V, P = 23,81 W | VENT; ficha ErP |
| ACS | sin sistema | SIS_Acs, caldera Saunier Duval Thema Condens 26 (26 kW, η 0,98 s/PCI), demanda 100,8 l/día a 60 °C | VENT hoja ACS; ficha caldera |
| Clima/refrig. | sin sistema | Daikin FTXC50C/RXC50C en P02_E01: 5,1 kW frío / 1,55 kW; 5,62 kW calor / 1,514 kW | catálogo Daikin |
| Superficie construida / cubierta | 32,5 | 63,0 / 63,0 | GEO |
| Puentes térmicos | longitudes de plantilla | longitudes estimadas (perímetro 32 m; esquinas 10 m; huecos); ψ sin cambios | estimación; HULC las recalcula |
| Localidad | Madrid, D3, 780 m | sin cambio | plantillas |

**Valores asumidos, no presentes en la documentación:** `capSenRefNom` = 0,65·capTot (valor por defecto del manual); ψ por defecto de la plantilla; resto de construcciones de la plantilla (muro F 1.013, suelo/forjados PIH_l7, cubierta Qifa_ue5); `INF-FLOW`/`PERCENTAGE-AIR-CHANGES` de la plantilla (los recalcula HULC).

**Validación (`validate_model.py`):** XML bien formado, CRLF, IDs únicos, referencias a construcciones/espacios/huecos existentes, polígonos antihorarios y cerrados, áreas > 0. Áreas: P01 63,0 · P02 E01 52,5 + E02 10,5 · P03 63,0 m²; huecos 10,53 m².

**Riesgos no verificables aquí:** que HULC acepte las etiquetas de sistema `SIS_Autonomo` (clase multizona ED) con una sola unidad interior, y que lea `datosVentilacion` con los valores de vivienda (la plantilla solo lo trae con tipo terciario). Si falla, ver INSTRUCCIONES_HULC.md (definir esos sistemas a mano).

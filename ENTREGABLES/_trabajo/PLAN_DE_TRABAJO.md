# PLAN DE TRABAJO — Grupo 9

## 1. Hallazgos de la Fase 1
1. `ENTREGABLES/Modelo Base CTE.dwg` es un dibujo AutoCAD, **no un .ctehexml**. No existe modelo HULC que revisar: el Caso base se construye desde cero, usando como plantilla `sesion_1_natalia_v2.ctehexml` (vivienda unifamiliar, UTF-8, CRLF) de «Versiones de HULC clase 2026» (decisión del usuario).
2. El «33 %» del encargo es en realidad **33 l/s** (caudal HS3, 3 dormitorios), no un porcentaje.
3. `Plano CAD.dxf` ya contiene capas P01 (huella 9×7), P02 (dos polígonos: 0–7,5 y 7,5–9) y P03 (polilínea con vértices intermedios). INSUNITS=4 (mm) con coordenadas en metros → se corregirá a metros.
4. El modelo de plantilla tiene errores respecto a este encargo (2 plantas habitables, bajocubierta acondicionado, 6,5×5 m, ventanas/puerta distintas) y se reconstruye.
5. **La documentación no contiene valores límite del DB-HE** (K, U, qsol;jul, n50, Cep,nren, Cep,tot) ni factores de paso. La red del entorno bloquea codigotecnico.org/BOE (WebFetch: ENOTFOUND). Solo la búsqueda web devuelve extractos de fuentes secundarias (p. ej. K_lim D, V/A≤1 = 0,53; V/A≥4 = 0,72, Normatia). → ver «Pendiente».

## 2. Puntos del enunciado → acción
| Nº | Exige (ENU) | Acción | Archivo | Verificación |
|---|---|---|---|---|
| 1 | Geometría y caso base; forjado sanitario y bajocubierta no habitables; verificar HE1 | Generar geometría (plantas P01 forjado, P02 vivienda 2 zonas, P03 bajocubierta) | DXF + Modelo Base CTE.ctehexml | Áreas ±1 % vs. DXF; XML bien formado |
| 2 | Ventilación 33 l/s, ACS 100,8 l/d, sistemas iniciales; **entregar ctehexml Caso base Madrid** | Sistemas: caldera Thema Condens (cal+ACS), split Daikin (refrig.), VMC Siber | Modelo Base CTE.ctehexml | Carga en HULC (usuario) |
| 3 | Sensibilidad por localidad (invierno/verano) | Solo HULC: variante de localidad documentada en INSTRUCCIONES_HULC.md | informe | marcadores [[RESULTADO HULC]] |
| 4 | Ventilación nocturna on/off; sustitución on/off | Solo HULC (casillas VentNoct, SistSust de DatosGenerales) | informe/instrucciones | marcadores |
| 5 | Qué cerramientos mejorar, valores razonables, referencias | calc_he1.py: U por capa, orden de impacto | calc_he1.py, informe | U ≤ U_lim |
| 6 | Reducir ψ razonadamente | Cambiar ψ en THERMAL-BRIDGE del modelo HE1 | Modelo HE1 | diff solo envolvente/PT |
| 7 | Cumplimiento HE1; no cumple aún HE0; **entregar ctehexml** | Iteraciones de envolvente | Modelo HE1 CTE.ctehexml | K ≤ 0,95·K_lim (estim.) |
| 8 | Equipos que más contribuyen a energía primaria; alternativa comercial | Estimación en calc_he0.py | informe | prestaciones = XML |
| 9 | FV con PVGIS, justificar superficie | Cálculo de cubierta SW (faldón a azimut 315° ± 90°) con PVGIS **no ejecutable** (red) → marcadores | informe | marcador PVGIS |
| 10 | Cumplimiento HE0; **entregar ctehexml** | Aerotermia + FV si procede | Modelo HE0 CTE.ctehexml | estimación con margen |
| Entrega | Memoria PDF `Trabajo_grupo9_2026.pdf` (el encargo pide «Informe Grupo 9.pdf»; se genera con el primero y se copia al segundo), ≤10 pág. + anexos, portada con Nº de grupo y **nombres de integrantes** (no suministrados → marcador) | Fase 6 | PDF | pypdf |

## 3. Supuestos
- S1: ventanas de F1 en el tramo acondicionado (0–7,5 m): puerta centrada en x = 3,75 m; 1 ventana a la izquierda y 2 a la derecha de la puerta, centradas en sus subtramos. Justificación: el enunciado no permite más precisión.
- S2: ventana de F3 centrada en el tramo acondicionado (x = 3,75 m); ventana de F2 en la zona no acondicionada (F2 está en x = 9); ventana de F4 centrada (y = 3,5).
- S3: el DXF se exporta con unidades en metros (INSUNITS=6).
- S4: Madrid/D3/780 m según plantillas de clase.
- S5: perfil de ocupación/uso Residencial del Anejo D, tipo de edificio Unifamiliar.
- S6: valores normativos: **pendiente de decisión** (ver abajo).

## 4. Orden de ejecución
Fase 2 (generador del Caso base) → Fase 3 (DXF) → Fase 4 (HE1) → Fase 5 (HE0) → Fase 6 (informe) → Fase 7 (diffs + instrucciones).

## 5. Pendiente
- Límites DB-HE: se necesitan las tablas oficiales (HE0 tablas 3.1.a/3.2.a, HE1 tablas 3.1.1.a y 3.1.1.b, apartado 3.1.3, factores de paso). Sin ellas, calc_he1.py y calc_he0.py llevarían límites no verificados.

# EvacSim

Simulador de evacuacion basado en agentes para analizar flujo peatonal, congestion y tiempos de salida en distintos escenarios.

## Estado del proyecto

Este proyecto esta orientado a entrega academica/tecnica: ejecutable por CLI y UI web (Dash), con pruebas unitarias y exportacion de metricas.

## Estructura del repositorio

```text
evacsim/
├── agents/            # Definicion del agente y perfiles de personalidad
├── behavior/          # Reglas de movimiento, estres y decision
├── crowd/             # Metricas locales de densidad, flujo y congestion
├── data/              # Exportacion y salida de resultados
├── engine/            # Nucleo de simulacion y carga de escenarios
├── environment/       # Grid, celdas, edificio y zonas
├── heatmaps/          # Seguimiento y exportacion de mapas de calor
├── metrics/           # Calculo y reporte de indicadores
├── routing/           # A*, BFS, Dijkstra y gestor de rutas
├── scenarios/         # Configuraciones scenario_1 ... scenario_6
├── tests/             # Suite de pruebas unitarias
├── ui/                # Aplicacion Dash y controlador UI
├── visualization/     # Render y graficas
├── config.py          # Constantes globales
└── main.py            # Punto de entrada CLI
```

## Requisitos

- Python 3.11 o superior
- pip actualizado

Dependencias en `requirements.txt`:

- mesa
- numpy
- matplotlib
- pandas
- dash
- plotly

## Instalacion

Desde la carpeta **padre** del paquete (ejemplo: `C:\Proyectos\LogicVac`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\evacsim\requirements.txt
```

## Ejecucion

### 1) Modo CLI

```powershell
python -m evacsim.main --list
python -m evacsim.main --scenario scenario_2 --steps 700 --export
python -m evacsim.main --scenario scenario_4 --visualize
```

Argumentos principales:

- `--scenario`: `scenario_1` a `scenario_6`
- `--steps`: maximo de ticks (default `500`)
- `--visualize`: render periodico en modo CLI
- `--export`: exporta CSV con resultados
- `--list`: lista escenarios disponibles

### 2) Modo UI (Dash)

```powershell
python -m evacsim.ui.app
```

Luego abrir: `http://127.0.0.1:8050`

## Pruebas

Ejecutar desde la carpeta padre del paquete:

```powershell
python -m unittest discover -s .\evacsim\tests -p "test_*.py"
```

## Ejemplos de uso

1. Comparar congestion entre escenarios:
   - correr `scenario_2` y `scenario_5` con igual `--steps`
   - exportar resultados y comparar `max_congestion` y `total_evacuation_time`
2. Analizar impacto de rutas:
   - en UI, alternar `A*`, `BFS` y `Dijkstra`
   - revisar cambios en ticks de evacuacion y bloqueos
3. Analizar trayectorias y mapa de calor:
   - activar trayectorias en UI
   - exportar imagen/CSV del heatmap para reporte

## Explicacion tecnica

La simulacion usa un modelo basado en agentes sobre un grid discreto. Cada tick:

1. cada agente evalua estado local (densidad, bloqueo, estres);
2. decide movimiento segun perfil y ruta calculada;
3. avanza (o espera) segun disponibilidad de celda;
4. se actualizan metricas globales y series historicas.

### Componentes clave

- `engine/simulation.py`: ciclo principal, scheduler y estado global.
- `routing/`: algoritmos de busqueda de camino.
- `metrics/`: agrega indicadores por tick y resumen final.
- `ui/simulation_controller.py`: integra simulacion, exportes y vistas.
- `visualization/renderer.py`: composicion del grid, agentes, heatmap y trayectorias.

## Convenciones y limpieza

- Archivos generados (`data/output`) y caches (`__pycache__`) estan ignorados por git.
- El paquete `tests` evita imports cruzados innecesarios para mejorar estabilidad de descubrimiento.
- Se recomienda mantener ejecucion via `python -m evacsim...` para consistencia de imports.

## Limitaciones actuales

- La simulacion es 2D en grid fijo (no multiescala/3D).
- Los escenarios son estaticos (sin cambios estructurales en tiempo real).
- La calibracion de parametros conductuales requiere ajuste para casos reales.

## Entregable recomendado

Para una entrega clara y reproducible:

1. incluir este README;
2. adjuntar 2-3 corridas exportadas (`CSV`/`JSON`) de escenarios distintos;
3. reportar comparativa de metricas (tiempo total, congestion maxima, eficiencia).

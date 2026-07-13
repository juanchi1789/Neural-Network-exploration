"""Build the four project notebooks from readable cell definitions."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source):
    return {
        "cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def write_notebook(name, cells):
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python (Neural Network Exploration)", "language": "python", "name": "neural-network-exploration"},
            "language_info": {"name": "python", "version": "3.8"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    (NOTEBOOKS / name).write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


IMPORTS = '''from pathlib import Path
import sys

# Funciona si el kernel inicia en la raíz o dentro de notebooks/.
PROJECT_ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import ipywidgets as widgets
from IPython.display import HTML, display, clear_output

from src.metrics import force_summary, neural_summary, population_activity
from src.muscle import normalize_force, spikes_to_force
from src.renshaw import simulate_renshaw_circuit
from src.visualization import animate_muscle_contraction, plot_raster, plot_renshaw_circuit, spike_times_from_matrix
'''


def notebook_03():
    cells = [
        md('''# 03 — Inhibición recurrente con células de Renshaw

## Objetivo

Construir un circuito neuromotor mínimo con un pool de motoneuronas (MN), un pool pequeño de células de Renshaw (R), excitación **MN → R** e inhibición recurrente **R → MN**.

Las motoneuronas usan inicialmente el preset *Regular Spiking*. Las Renshaw usan *Fast Spiking* como **aproximación funcional** para representar una interneurona rápida; no es una calibración biológica específica ni permite inferencias cuantitativas sobre células de Renshaw reales.'''),
        code(IMPORTS),
        md('''## Convención de pesos y corrientes

Las filas de cada matriz son neuronas de origen y las columnas son neuronas de destino. `W_MN_to_R` y `W_R_to_MN` guardan **magnitudes positivas**. La segunda matriz es inhibitoria por su uso en la ecuación, no por su signo:

\[
I_{MN}=I_{motor}+I_{ruido}-I_{Renshaw},\qquad
I_R=I_{MN\to R}+I_{ruido,R}.
\]

Cada spike incrementa una variable sináptica que decae exponencialmente con `tau_syn`. La integración neuronal es Euler y el reset se aplica cuando `v ≥ 30 mV`.'''),
        code('''def plot_renshaw_results(results, bin_size_ms=20):
    """Muestra arquitectura, matrices y las señales pedidas en un panel."""
    t = results["time"]
    dt = results["dt"]
    mn_times = spike_times_from_matrix(results["spikes_MN"], t)
    r_times = spike_times_from_matrix(results["spikes_R"], t)
    bins_mn, activity_mn = population_activity(results["spikes_MN"], dt, bin_size_ms)
    bins_r, activity_r = population_activity(results["spikes_R"], dt, bin_size_ms)
    fig, axes = plt.subplots(3, 3, figsize=(17, 13))
    plot_renshaw_circuit(results["W_MN_to_R"], results["W_R_to_MN"], axes[0, 0])
    for ax, matrix, title in [(axes[0,1], results["W_MN_to_R"], "W_MN_to_R (+)"),
                              (axes[0,2], results["W_R_to_MN"], "W_R_to_MN (magnitud +)")]:
        im = ax.imshow(matrix, aspect="auto", cmap="viridis", origin="lower")
        ax.set(title=title, xlabel="Destino", ylabel="Origen"); fig.colorbar(im, ax=ax, shrink=.75)
    plot_raster(mn_times, axes[1,0]); axes[1,0].set_title("Raster de motoneuronas")
    plot_raster(r_times, axes[1,1]); axes[1,1].set_title("Raster de Renshaw")
    axes[1,2].plot(t, results["I_R_to_MN"].mean(axis=0), color="tab:red")
    axes[1,2].set(title="Inhibición media recibida por MN", xlabel="Tiempo (ms)", ylabel="Corriente (u.a.)")
    axes[2,0].plot(t, results["V_MN"][0]); axes[2,0].set_title("v de MN representativa")
    axes[2,1].plot(t, results["V_R"][0], color="tab:orange"); axes[2,1].set_title("v de Renshaw representativa")
    axes[2,2].step(bins_mn, activity_mn, where="post", label="MN")
    axes[2,2].step(bins_r, activity_r, where="post", label="Renshaw")
    axes[2,2].set(title=f"Actividad poblacional ({bin_size_ms} ms)", xlabel="Tiempo (ms)", ylabel="Spikes/bin"); axes[2,2].legend()
    for ax in axes.flat: ax.grid(alpha=.2)
    fig.tight_layout(); plt.show()
'''),
        md('''## GUI

Cada fila define brevemente el parámetro antes de mostrar su control. Los límites pequeños protegen la velocidad y legibilidad de las figuras.'''),
        code('''def described_widget(text, widget):
    label = widgets.HTML(f"<div style='width:310px;font-size:13px'>{text}</div>")
    return widgets.HBox([label, widget])

controls_spec = {
    "n_motor": ("<b>Motoneuronas</b><br>Tamaño del pool motor (2–30).", widgets.IntSlider(value=20, min=2, max=30)),
    "n_renshaw": ("<b>Células de Renshaw</b><br>Tamaño del pool inhibitorio (1–10).", widgets.IntSlider(value=5, min=1, max=10)),
    "amplitude": ("<b>Comando motor</b><br>Amplitud del input externo común.", widgets.FloatSlider(value=12, min=0, max=30, step=.5)),
    "input_type": ("<b>Tipo de input</b><br>Forma temporal del comando.", widgets.Dropdown(options=["constant","pulse","ramp","sinusoidal","motor_plan"], value="motor_plan")),
    "parameter_noise": ("<b>Ruido de parámetros</b><br>Heterogeneidad relativa de a, b, c y d.", widgets.FloatSlider(value=.03, min=0, max=.2, step=.01)),
    "input_noise": ("<b>Ruido de input</b><br>Desvío del ruido individual de corriente.", widgets.FloatSlider(value=.5, min=0, max=5, step=.1)),
    "p_mn_to_r": ("<b>Probabilidad MN → R</b><br>Densidad de conexiones excitatorias.", widgets.FloatSlider(value=.5, min=0, max=1, step=.05)),
    "w_mn_to_r": ("<b>Peso MN → R</b><br>Magnitud de excitación por conexión.", widgets.FloatSlider(value=1.5, min=0, max=5, step=.1)),
    "p_r_to_mn": ("<b>Probabilidad R → MN</b><br>Densidad del feedback inhibitorio.", widgets.FloatSlider(value=.6, min=0, max=1, step=.05)),
    "w_r_to_mn": ("<b>Peso R → MN</b><br>Magnitud que se resta al input motor.", widgets.FloatSlider(value=1., min=0, max=8, step=.1)),
    "synaptic_tau": ("<b>Constante sináptica</b><br>Decaimiento exponencial en ms.", widgets.FloatSlider(value=10, min=1, max=50, step=1)),
    "total_time": ("<b>Duración</b><br>Tiempo total de simulación (ms).", widgets.IntSlider(value=1000, min=300, max=2000, step=100)),
    "dt": ("<b>dt</b><br>Paso de Euler en ms.", widgets.FloatSlider(value=.5, min=.1, max=1, step=.1)),
    "seed": ("<b>Semilla</b><br>Permite repetir conectividad y ruido.", widgets.IntSlider(value=42, min=0, max=999)),
    "recurrent_inhibition": ("<b>Inhibición recurrente</b><br>Activa o desconecta R → MN.", widgets.Checkbox(value=True)),
}
output = widgets.Output()
button = widgets.Button(description="Simular circuito", button_style="success")

def run_gui(_=None):
    with output:
        clear_output(wait=True)
        kwargs = {name: item[1].value for name, item in controls_spec.items()}
        results = simulate_renshaw_circuit(**kwargs)
        print(f"Spikes MN: {results['spikes_MN'].sum()} | Spikes R: {results['spikes_R'].sum()}")
        plot_renshaw_results(results)

button.on_click(run_gui)
display(widgets.VBox([widgets.HTML("<h3>Controles del circuito MN–Renshaw</h3>"),
                      *[described_widget(text, widget) for text, widget in controls_spec.values()], button]), output)
'''),
        md('''## Supuestos y límites

- Los pesos y unidades de corriente son abstractos; no están ajustados a datos experimentales.
- Las conexiones son Bernoulli aleatorias y no incluyen retardos ni plasticidad.
- RS y FS son proxies funcionales. El circuito permite estudiar comportamiento cualitativo, no reproducir exactamente un circuito espinal.'''),
    ]
    write_notebook("03_recurrent_inhibition_renshaw.ipynb", cells)


def notebook_04():
    cells = [
        md('''# 04 — Experimentos comparativos de inhibición Renshaw

Se compara **el mismo circuito** bajo cuatro magnitudes de `W_R_to_MN`. Input, tamaños, parámetros base, ruido, conectividad aleatoria, semilla, duración y `dt` permanecen constantes. En el escenario control se desconecta la inhibición; las Renshaw pueden seguir activándose, pero su corriente no se resta a las motoneuronas.'''),
        code(IMPORTS),
        code('''BASE = dict(
    n_motor=20, n_renshaw=5, amplitude=12.0, input_type="motor_plan",
    parameter_noise=.03, input_noise=.5, p_mn_to_r=.5, w_mn_to_r=1.5,
    p_r_to_mn=.6, synaptic_tau=10., total_time=1000., dt=.5, seed=42,
)
SCENARIOS = {
    "Sin inhibición": dict(w_r_to_mn=0.0, recurrent_inhibition=False),
    "Débil": dict(w_r_to_mn=0.5, recurrent_inhibition=True),
    "Moderada": dict(w_r_to_mn=1.5, recurrent_inhibition=True),
    "Fuerte": dict(w_r_to_mn=4.0, recurrent_inhibition=True),
}

results = {}
rows = []
for name, change in SCENARIOS.items():
    result = simulate_renshaw_circuit(**BASE, **change)
    results[name] = result
    row = neural_summary(result["spikes_MN"], result["time"], result["I_R_to_MN"])
    row.update({"escenario": name, "peso_R_a_MN": change["w_r_to_mn"]})
    rows.append(row)

comparison = pd.DataFrame(rows).set_index("escenario")
comparison
'''),
        md('''La corriente inhibitoria media incluye toda la duración, también los períodos sin actividad. El ISI se agrupa a partir de los intervalos intra-neurona disponibles; no se crean intervalos entre neuronas distintas.'''),
        code('''fig, axes = plt.subplots(2, 2, figsize=(14, 9))
comparison["firing_rate_medio_Hz"].plot.bar(ax=axes[0,0], color="steelblue", title="Firing rate medio")
comparison["spikes_totales"].plot.bar(ax=axes[0,1], color="slateblue", title="Spikes totales")
comparison["corriente_inhibitoria_media"].plot.bar(ax=axes[1,0], color="firebrick", title="Corriente inhibitoria media")
for name, result in results.items():
    bins, activity = population_activity(result["spikes_MN"], result["dt"], 20)
    axes[1,1].step(bins, activity, where="post", label=name, alpha=.8)
axes[1,1].set_title("Actividad poblacional superpuesta"); axes[1,1].legend()
for ax in axes.flat:
    ax.grid(alpha=.25); ax.set_xlabel("")
fig.tight_layout(); plt.show()
'''),
        code('''fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
for ax, name in zip(axes, ["Sin inhibición", "Moderada"]):
    result = results[name]
    plot_raster(spike_times_from_matrix(result["spikes_MN"], result["time"]), ax)
    ax.set_title(name)
fig.suptitle("Raster MN: control frente a inhibición moderada")
fig.tight_layout(); plt.show()
'''),
        md('''## Preguntas para interpretar la ejecución

- ¿La inhibición reduce la actividad del pool motor en esta realización?
- ¿La inhibición fuerte suprime excesivamente la respuesta o aún conserva actividad?
- ¿Cómo cambian el ISI medio y su variabilidad?
- ¿Se observa una regulación progresiva al aumentar el peso?

No se presupone monotonicidad ni “mayor estabilidad”. Las respuestas deben basarse en la tabla, los rasters y las curvas que produjo esta ejecución; otra semilla o parametrización puede cambiar el patrón.'''),
    ]
    write_notebook("04_renshaw_comparison_experiments.ipynb", cells)


def notebook_05():
    cells = [
        md('''# 05 — De spikes a fuerza muscular simplificada

Cada spike del pool motor genera un *twitch* causal:

\[
h(t)=A\\left(e^{-t/\\tau_{\\mathrm{decay}}}-e^{-t/\\tau_{\\mathrm{rise}}}\\right),\\quad t \\ge 0
\]

La señal de fuerza es la suma lineal de todos los twitches. Es un proxy de activación/contracción, no un modelo de unidades motoras, fatiga, longitud-tensión o biomecánica articular.'''),
        code(IMPORTS),
        code('''BASE = dict(n_motor=20, n_renshaw=5, amplitude=12., input_type="motor_plan",
            parameter_noise=.03, input_noise=.5, p_mn_to_r=.5, w_mn_to_r=1.5,
            p_r_to_mn=.6, synaptic_tau=10., total_time=1000., dt=.5, seed=42)
SCENARIOS = {
    "Sin Renshaw": dict(w_r_to_mn=0., recurrent_inhibition=False),
    "Moderada": dict(w_r_to_mn=1.5, recurrent_inhibition=True),
    "Fuerte": dict(w_r_to_mn=4., recurrent_inhibition=True),
}
results, forces, summaries = {}, {}, []
for name, change in SCENARIOS.items():
    result = simulate_renshaw_circuit(**BASE, **change)
    force = spikes_to_force(result["spikes_MN"], result["time"], amplitude=1., tau_rise_ms=10., tau_decay_ms=50.)
    results[name], forces[name] = result, force
    summaries.append({"escenario": name, **force_summary(force, result["time"])})
force_table = pd.DataFrame(summaries).set_index("escenario")
force_table
'''),
        code('''fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
reference = results["Moderada"]
plot_raster(spike_times_from_matrix(reference["spikes_MN"], reference["time"]), axes[0])
axes[0].set_title("Raster de motoneuronas — inhibición moderada")
for name, force in forces.items():
    axes[1].plot(reference["time"], force, label=name)
axes[1].set(title="Fuerza muscular estimada", xlabel="Tiempo (ms)", ylabel="Fuerza (u.a.)")
axes[1].legend(); axes[1].grid(alpha=.25)
fig.tight_layout(); plt.show()
'''),
        md('''## Visualización 2D de contracción

La elipse se acorta y ensancha según la fuerza normalizada. Es deliberadamente esquemática: representa activación/contracción visual, **no anatomía real** ni movimiento de una extremidad.'''),
        code('''moderate_force = normalize_force(forces["Moderada"])
muscle_animation = animate_muscle_contraction(results["Moderada"]["time"], moderate_force)
plt.close(muscle_animation._fig)  # evita una figura estática duplicada
display(HTML(muscle_animation.to_jshtml()))
'''),
        md('''## Lectura prudente

En este modelo lineal, menos spikes normalmente producen menos suma de twitches, pero la forma temporal también depende de cuándo ocurren. Las métricas (`max_force`, `mean_force`, `time_to_peak_ms`) describen únicamente esta señal artificial.'''),
    ]
    write_notebook("05_spikes_to_muscle_force.ipynb", cells)


def notebook_06():
    cells = [
        md('''# Simulación progresiva de un circuito neuromotor mediante neuronas de Izhikevich

## Objetivo general

El proyecto avanza desde una neurona individual hasta un circuito simplificado de motoneuronas y células de Renshaw. Su propósito es explorar cómo input, heterogeneidad y conectividad modifican la actividad spiking, y cómo esa actividad puede transformarse en una salida muscular estimada.'''),
        code(IMPORTS),
        md('''## Etapas del proyecto

```mermaid
flowchart TD
    A[Neurona individual] --> B[Pool neuronal]
    B --> C[Matriz de conectividad W]
    C --> D[Pool de motoneuronas]
    D --> E[Células de Renshaw]
    E --> F[Inhibición recurrente]
    F --> G[Salida muscular simplificada]
```'''),
        md('''## Modelo de Izhikevich

\[
\frac{dv}{dt}=0.04v^2+5v+140-u+I,\qquad
\frac{du}{dt}=a(bv-u)
\]

- `v`: potencial de membrana; `u`: variable de recuperación.
- `I`: corriente externa, ruido y, cuando corresponde, corriente sináptica.
- `a`: velocidad de recuperación; `b`: acoplamiento de `u` con `v`.
- `c`: voltaje de reset; `d`: incremento de recuperación después del spike.
- Si `v ≥ 30 mV`, se registra un spike y se aplica `v = c`, `u = u + d`.

La integración de Euler prioriza transparencia y velocidad en estas simulaciones pequeñas.'''),
        md('''## Resultados principales

El panel siguiente vuelve a ejecutar solamente dos condiciones compactas para reunir figuras representativas. Los detalles interactivos y análisis completos permanecen en las notebooks 01–05.'''),
        code('''BASE = dict(n_motor=20, n_renshaw=5, amplitude=12., parameter_noise=.03, input_noise=.5,
            p_mn_to_r=.5, w_mn_to_r=1.5, p_r_to_mn=.6, synaptic_tau=10.,
            total_time=1000., dt=.5, seed=42, input_type="motor_plan")
control = simulate_renshaw_circuit(**BASE, w_r_to_mn=0., recurrent_inhibition=False)
moderate = simulate_renshaw_circuit(**BASE, w_r_to_mn=1.5, recurrent_inhibition=True)
force = spikes_to_force(moderate["spikes_MN"], moderate["time"])

summary_table = pd.DataFrame([
    {"escenario": "Sin inhibición", **neural_summary(control["spikes_MN"], control["time"], control["I_R_to_MN"])},
    {"escenario": "Moderada", **neural_summary(moderate["spikes_MN"], moderate["time"], moderate["I_R_to_MN"])},
]).set_index("escenario")
display(summary_table)

fig, axes = plt.subplots(2, 4, figsize=(20, 9))
axes[0,0].plot(control["time"], control["V_MN"][0]); axes[0,0].set_title("Neurona individual representativa")
plot_raster(spike_times_from_matrix(control["spikes_MN"], control["time"]), axes[0,1]); axes[0,1].set_title("Raster del pool")
im = axes[0,2].imshow(moderate["W_R_to_MN"], aspect="auto", origin="lower", cmap="viridis")
axes[0,2].set(title="Matriz W_R_to_MN", xlabel="MN destino", ylabel="R origen"); fig.colorbar(im, ax=axes[0,2])
plot_renshaw_circuit(moderate["W_MN_to_R"], moderate["W_R_to_MN"], axes[0,3], show_labels=False)
for ax, result, title in [(axes[1,0], control, "Sin inhibición"), (axes[1,1], moderate, "Inhibición moderada")]:
    plot_raster(spike_times_from_matrix(result["spikes_MN"], result["time"]), ax); ax.set_title(title)
axes[1,2].plot(moderate["time"], force, color="firebrick"); axes[1,2].set_title("Salida muscular simplificada")
bins, activity = population_activity(moderate["spikes_MN"], moderate["dt"], 20)
axes[1,3].step(bins, activity, where="post"); axes[1,3].set_title("Actividad poblacional")
for ax in axes.flat: ax.grid(alpha=.2)
fig.tight_layout(); plt.show()
'''),
        md('''## Conclusiones

- El modelo de Izhikevich permite generar varios patrones de disparo con pocas variables y bajo costo computacional.
- El input controla el régimen de activación; el ruido y la heterogeneidad evitan que todo el pool responda de forma idéntica.
- La matriz `W` hace explícitas dirección, densidad y magnitud de las interacciones.
- En este circuito, el efecto observado de la inhibición recurrente debe leerse en la tabla y los rasters de la ejecución: no se asume que siempre estabilice o reduzca monótonamente la actividad.
- La fuerza simplificada integra temporalmente los spikes; conecta salida neuronal y una señal contráctil, pero no equivale a fuerza muscular experimental.'''),
        md('''## Limitaciones

- Parámetros no calibrados específicamente con datos experimentales.
- Conexiones aleatorias e input motor artificial.
- Representación simplificada de motoneuronas y Renshaw con presets RS/FS.
- Modelo muscular lineal y no biomecánico.
- Sin feedback sensorial, músculo antagonista, retardos axonales, plasticidad ni fatiga.'''),
        md('''## Trabajo futuro

- Calibrar parámetros y conectividad con bibliografía y datos.
- Agregar inhibición recíproca y pools agonista–antagonista.
- Incorporar huso neuromuscular y órgano tendinoso de Golgi.
- Implementar feedback sensorial, retardos y unidades motoras heterogéneas.
- Mejorar la visualización muscular y, recién después, conectarla con biomecánica.'''),
    ]
    write_notebook("06_project_summary.ipynb", cells)


if __name__ == "__main__":
    notebook_03(); notebook_04(); notebook_05(); notebook_06()
    from enrich_notebook_explanations import enrich_all
    enrich_all()

"""Insert an idempotent explanatory layer into notebooks 01–06.

The script preserves all existing code, outputs and user-authored cells. Cells
created here are tagged with ``explanation_pack=v2`` so they can be refreshed
without duplication.
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
TAG = "v2"


def markdown(text):
    return {
        "cell_type": "markdown",
        "metadata": {"explanation_pack": TAG},
        "source": text.strip().splitlines(keepends=True),
    }


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"explanation_pack": TAG},
        "outputs": [],
        "source": text.strip().splitlines(keepends=True),
    }


NB01_INTRO = r"""
## Cómo leer esta notebook

Esta primera etapa responde dos preguntas diferentes:

1. **¿Cómo se comporta una neurona de Izhikevich aislada?** Se observa cómo el input modifica `v`, `u` y los spikes.
2. **¿Qué cambia al simular muchas neuronas independientes?** Todas reciben el mismo comando, pero el ruido y las pequeñas diferencias de parámetros evitan respuestas idénticas.

El recorrido conceptual es:

```text
tipo de input + amplitud
          ↓
 corriente I(t)
          ↓
 ecuaciones de Izhikevich
          ↓
 potencial v(t) y recuperación u(t)
          ↓
 si v ≥ 30 mV: registrar spike y aplicar reset
```

Todavía no hay conexiones sinápticas entre neuronas. Esta notebook valida los bloques elementales que usarán las siguientes.
"""

NB01_SINGLE = r"""
### Qué observar en la neurona individual

- **Potencial `v(t)`**: la variable rápida que produce el spike. El pico dibujado en 30 mV es un marcador; después se aplica `v = c`.
- **Recuperación `u(t)`**: resume procesos lentos que frenan o adaptan el disparo. Después de un spike aumenta en `d`.
- **Input `I(t)`**: no es voltaje ni fuerza; es la corriente externa abstracta que impulsa el modelo.
- **Spikes totales**: cantidad de veces que se alcanzó el umbral.
- **Firing rate**: spikes por segundo durante toda la simulación. Si hay largos períodos de reposo, esta tasa será menor que la calculada solo durante el estímulo.

Los presets cambian `a`, `b`, `c` y `d`. En el proyecto se usan como patrones funcionales; no representan una calibración específica de una motoneurona real.
"""

NB01_POOL = r"""
## Del caso individual al pool independiente

En un pool, cada fila de `V` y `spikes` corresponde a una neurona y cada columna a un instante temporal.

### ¿Qué significa la semilla aleatoria?

La simulación usa números aleatorios para generar:

- pequeñas variaciones de `a`, `b`, `c` y `d`;
- ruido individual en la corriente.

La **semilla** (`random_seed`) es el punto de inicio de ese generador pseudoaleatorio. No es una propiedad biológica ni un parámetro neuronal.

```text
misma semilla + mismos parámetros → exactamente la misma realización
otra semilla                    → otro ruido y otra heterogeneidad
```

Fijarla permite comparar dos condiciones sin que el cambio observado se deba a haber sorteado otro ruido. Para evaluar robustez se repite el experimento con muchas semillas y se resumen media y dispersión.
"""

NB01_METRICS = r"""
### Cómo leer las visualizaciones poblacionales

- **Raster**: una fila por neurona; cada marca vertical es un spike. Permite ver sincronía, silencios y distribución temporal.
- **Mapa de calor**: muestra el potencial de todas las neuronas, no solo los spikes.
- **Actividad poblacional**: suma los spikes dentro de ventanas de tiempo (`bin_size_ms`). Un bin grande suaviza la señal; uno pequeño conserva más detalle y fluctúa más.
- **Neuronas activas**: neuronas que dispararon al menos una vez. No informa cuántas veces disparó cada una.

El pool de esta sección sigue siendo independiente: similitudes entre filas provienen del input común, no de conexiones entre neuronas.
"""

NB02_INTRO = r"""
## Qué agrega esta notebook

Ahora las neuronas dejan de ser independientes. Un spike de una neurona puede modificar la corriente de otra mediante una matriz de conectividad `W`.

```text
input externo ───────────────┐
ruido individual ────────────┼→ corriente total → dinámica neuronal → spikes
spikes de otras neuronas → W ┘                                  │
                          ↑_______________________________________┘
```

La realimentación aparece porque los spikes actualizan estados sinápticos que vuelven a entrar como corriente en pasos posteriores.
"""

NB02_MATRIX = r"""
### Cómo leer la matriz `W`

La convención de esta notebook es:

```text
W[i, j] = efecto de la neurona origen i sobre la neurona destino j
```

Ejemplo para tres neuronas:

| Origen \ Destino | N1 | N2 | N3 |
|---|---:|---:|---:|
| N1 | 0 | +0.5 | 0 |
| N2 | 0 | 0 | −0.8 |
| N3 | +0.3 | 0 | 0 |

- `W[0,1]=+0.5`: un estado sináptico de N1 excita a N2.
- `W[1,2]=−0.8`: N2 inhibe a N3.
- `0`: no existe esa conexión.
- La diagonal se anula para evitar autoconexiones.

La matriz no contiene spikes ni corrientes temporales: contiene **la arquitectura y magnitud de las conexiones**.
"""

NB02_DYNAMICS = r"""
### Qué ocurre en cada paso temporal

1. La variable sináptica `S` decae exponencialmente.
2. Se calcula `I_syn = W.T @ S`. La transpuesta convierte estados de origen en corrientes de destino.
3. Se suman input externo, ruido y corriente sináptica.
4. Euler actualiza `v` y `u`.
5. Las neuronas que alcanzan 30 mV registran un spike y se resetean.
6. Cada spike incrementa su estado `S`, que influirá sobre la red.

`synaptic_tau` controla cuánto dura ese efecto. Una constante mayor hace que la influencia de un spike desaparezca más lentamente.

La semilla fija simultáneamente parámetros, conectividad y ruido. Por eso dos configuraciones comparadas con la misma semilla comparten la misma realización aleatoria.
"""

NB02_METRICS = r"""
### Interpretación y límites

- La **corriente sináptica media** puede ocultar que algunas neuronas reciben excitación y otras inhibición; conviene leerla junto con `W`.
- Un aumento de actividad poblacional no implica necesariamente sincronización: el raster muestra si los spikes coinciden temporalmente.
- La probabilidad de conexión controla densidad; `weight_scale` controla magnitud. Son conceptos distintos.
- Esta red usa sinapsis de corriente simplificadas, sin potenciales de reversión, retardos axonales ni plasticidad.
"""

NB03_INTRO = r"""
## Pregunta central y rol de la semilla

Esta notebook pregunta: **¿puede un grupo de interneuronas activado por las motoneuronas devolver una corriente que limite su actividad posterior?**

La semilla fija, en un mismo orden reproducible:

1. heterogeneidad de las motoneuronas;
2. heterogeneidad de las Renshaw;
3. conexiones `MN → R`;
4. conexiones `R → MN`;
5. ruido de ambos pools.

Así, activar o desactivar la inhibición con la misma semilla compara el mismo circuito y el mismo ruido. La semilla 42 no es “mejor”: es solo una realización reproducible.

### Flujo causal del circuito
"""

NB03_FLOW_CODE = """
from src.visualization import plot_renshaw_signal_flow

plot_renshaw_signal_flow()
plt.show()
"""

NB03_MATRICES = r"""
## Las dos matrices de Renshaw, paso a paso

Con 20 motoneuronas y 5 células de Renshaw:

- `W_MN_to_R.shape == (20, 5)`
- `W_R_to_MN.shape == (5, 20)`

Siempre se usa **fila = origen** y **columna = destino**.

### `W_MN_to_R`

`W_MN_to_R[i, j]` indica cuánto excita la motoneurona `i` a la Renshaw `j`. Sus valores son magnitudes positivas.

### `W_R_to_MN`

`W_R_to_MN[k, i]` indica la magnitud con que la Renshaw `k` inhibe a la motoneurona `i`. También se almacena positiva, pero el modelo la resta:

\[
I_{MN,i}=I_{motor}+I_{ruido,i}-\sum_k W_{R\to MN}[k,i]S_{R,k}
\]

Ejemplo: si una Renshaw tiene estado `S=2` y su peso hacia una MN es `1.5`, aporta una magnitud inhibitoria `3.0`, que se resta del input de esa MN.

Esta convención evita mezclar pesos negativos con una segunda resta. El signo biológico está en la ecuación, no en el valor guardado en la matriz.
"""

NB03_RESULTS = r"""
## Cómo leer el panel de resultados

1. **Diagrama**: muestra qué conexiones existen, no cuándo están activas.
2. **Matrices**: permiten localizar origen, destino y magnitud.
3. **Raster MN y R**: comprueba la secuencia esperada: actividad MN, activación Renshaw y modificación posterior de MN.
4. **Voltajes representativos**: muestran la dinámica individual, pero una neurona no resume todo el pool.
5. **Actividad poblacional**: suma spikes por bin; depende del tamaño del bin.
6. **Corriente inhibitoria media**: promedio entre todas las MN y todo el tiempo. Incluye períodos de reposo, por lo que no equivale al máximo feedback durante el estímulo.

Una inhibición mayor puede reducir spikes sin silenciar todas las neuronas. El resultado debe describirse como comportamiento de este modelo, no como medición fisiológica.
"""

NB04_INTRO = r"""
## Por qué esta comparación es un experimento controlado

Los cuatro escenarios conservan:

- input motor;
- tamaños de los pools;
- parámetros base y nivel de heterogeneidad;
- ruido;
- máscaras de conectividad;
- duración, `dt` y semilla.

Solo cambia el peso `R → MN`. Por eso una diferencia entre escenarios puede atribuirse dentro del modelo a la intensidad de esa vía, y no a otro sorteo aleatorio.

Una sola semilla describe una realización. Para afirmar robustez conviene repetir todas las condiciones con varias semillas y mostrar media, desviación estándar o distribuciones.
"""

NB04_METRICS = r"""
## Qué significa cada métrica

| Métrica | Cálculo | Qué informa | Qué no informa |
|---|---|---|---|
| Spikes totales | suma de la matriz binaria | salida total del pool | distribución entre neuronas |
| Firing rate medio | spikes / neuronas / segundos | frecuencia media del ensayo completo | tasa exclusiva durante el estímulo |
| MN activas | filas con ≥1 spike | reclutamiento mínimo | intensidad de cada MN |
| Pico poblacional | máximo de spikes por bin | mayor concentración temporal | sincronía exacta; depende del bin |
| Corriente inhibitoria media | promedio de `I_R_to_MN` | nivel global de feedback | máximos o diferencias entre MN |
| ISI medio | media de intervalos intra-neurona | separación temporal típica | regularidad por sí sola |
| Variabilidad ISI | desvío estándar agrupado | dispersión de intervalos | una prueba universal de estabilidad |

Las métricas se complementan. Por ejemplo, dos escenarios pueden tener igual cantidad de spikes pero diferente distribución temporal y, por lo tanto, distinta fuerza máxima.
"""

NB04_READING = r"""
### Cómo formular la conclusión

Una conclusión válida tiene esta forma:

> “Con esta parametrización y esta semilla, aumentar el peso inhibitorio produjo X cambio en spikes, firing rate e ISI.”

Una conclusión demasiado fuerte sería:

> “Las células de Renshaw siempre estabilizan el sistema motor.”

Para generalizar se necesitan múltiples semillas, análisis de sensibilidad y parámetros con respaldo experimental. La ausencia de monotonicidad en alguna métrica no invalida el circuito: puede surgir de la interacción temporal entre spikes, feedback y bins.
"""

NB05_INTRO = r"""
## Por qué se usa este twitch

Un spike neuronal es un evento muy breve, pero una contracción muscular elemental sube y decae más lentamente. La diferencia de exponenciales proporciona ese perfil con dos parámetros interpretables:

\[
h(t)=A\left(e^{-t/\tau_{decay}}-e^{-t/\tau_{rise}}\right),\quad t\ge 0
\]

- `tau_rise`: subida rápida de la respuesta.
- `tau_decay`: relajación más lenta; debe ser mayor que `tau_rise`.
- `A`: escala del twitch. En `twitch_response` el kernel se normaliza para que su pico coincida con la amplitud solicitada.

Se eligió porque es causal, simple, positiva con `tau_decay > tau_rise`, fácil de visualizar y suficiente para estudiar sumación temporal. No modela calcio, reclutamiento de unidades motoras, fatiga ni relación longitud–tensión.

### Flujo spikes → fuerza
"""

NB05_FLOW_CODE = """
from src.visualization import plot_spikes_to_force_flow

plot_spikes_to_force_flow()
plt.show()
"""

NB05_CONVERSION = r"""
## Cómo se convierten los spikes en fuerza

La matriz `spikes_MN` tiene forma `(motoneuronas, tiempo)` y contiene `True/1` cuando una MN dispara.

1. Se suman las filas para obtener impulsos poblacionales por instante.
2. Se construye el kernel twitch para el mismo `dt`.
3. Se aplica una convolución causal:

\[
F[t]=\sum_{k=0}^{t} impulses[k]h[t-k]
\]

4. Si llegan varios spikes antes de que el twitch anterior decaiga, sus respuestas se superponen y la fuerza aumenta.

Ejemplo conceptual:

```text
spike aislado       → un twitch aislado
spikes cercanos     → twitches superpuestos → mayor pico
menos spikes        → normalmente menor fuerza media
mismo nº de spikes  → el pico puede cambiar si cambia su timing
```

La fuerza está en unidades arbitrarias. Como es una transformación determinista de los spikes, no constituye una validación independiente del circuito neuronal.
"""

NB05_METRICS = r"""
## Métricas musculares

- **Fuerza máxima**: mayor suma instantánea de twitches. Es sensible al agrupamiento temporal de spikes.
- **Fuerza media**: promedio de toda la señal, incluyendo reposo. Está fuertemente relacionada con la cantidad total de spikes.
- **Tiempo hasta el pico**: instante del máximo global; puede cambiar aunque la fuerza media siga una tendencia regular.
- **Fuerza normalizada**: divide por el máximo para obtener valores entre 0 y 1. Sirve para animación, pero elimina diferencias absolutas entre escenarios.

La elipse animada traduce la activación normalizada a ancho y largo. Es una metáfora visual de contracción, no una reconstrucción anatómica.
"""

NB06_INTRO = r"""
## Cómo presentar el proyecto

La contribución central no es proponer una nueva fisiología, sino construir un pipeline progresivo, transparente y reproducible:

```text
dinámica individual → actividad poblacional → interacción sináptica
→ feedback recurrente → comparación controlada → salida contráctil
```

La notebook final selecciona figuras representativas; los detalles y controles permanecen en las notebooks anteriores. Durante una presentación conviene distinguir siempre:

- **implementación**: qué calcula el código;
- **resultado**: qué ocurrió en esta simulación;
- **interpretación**: qué mecanismo conceptual ilustra;
- **limitación**: por qué no debe extrapolarse directamente a biología real.
"""

NB06_RESULTS = r"""
## Lectura integrada de los resultados

El circuito implementado muestra que el feedback Renshaw puede modificar la salida del pool motor. La señal muscular hereda esos cambios porque se calcula directamente a partir de los spikes.

La conclusión más sólida es cualitativa y acotada:

> Dentro de este modelo, manteniendo constante la realización aleatoria, aumentar la magnitud inhibitoria reduce modestamente la actividad total y la fuerza media, aunque no todas las métricas temporales cambian de manera monotónica.

Para fortalecer esa afirmación se recomienda repetir el experimento con varias semillas, reportar dispersión y comprobar sensibilidad a `dt`, pesos, probabilidades y constante sináptica.
"""


PACKS = {
    "01_izhikevich_neuron.ipynb": [
        ("# 01 - Single Izhikevich Neuron", [markdown(NB01_INTRO)]),
        ("interact(\n    plot_simulation", [markdown(NB01_SINGLE)]),
        ("# 02 - Pull of Izhikevich Neurons", [markdown(NB01_POOL)]),
        ("def compute_population_activity", [markdown(NB01_METRICS)]),
    ],
    "02_neuron_interaction_W.ipynb": [
        ("# Neuron Interaction", [markdown(NB02_INTRO)]),
        ("def create_connectivity_matrix", [markdown(NB02_MATRIX)]),
        ("def simulate_connected_izhikevich_network", [markdown(NB02_DYNAMICS)]),
        ("def compute_population_activity", [markdown(NB02_METRICS)]),
    ],
    "03_recurrent_inhibition_renshaw.ipynb": [
        ("# 03 — Inhibición recurrente", [markdown(NB03_INTRO)]),
        ("from src.visualization import animate_muscle_contraction", [code(NB03_FLOW_CODE)]),
        ("## Convención de pesos y corrientes", [markdown(NB03_MATRICES)]),
        ("def plot_renshaw_results", [markdown(NB03_RESULTS)]),
    ],
    "04_renshaw_comparison_experiments.ipynb": [
        ("# 04 — Experimentos comparativos", [markdown(NB04_INTRO)]),
        ("comparison = pd.DataFrame", [markdown(NB04_METRICS)]),
        ("fig.suptitle(\"Raster MN", [markdown(NB04_READING)]),
    ],
    "05_spikes_to_muscle_force.ipynb": [
        ("# 05 — De spikes a fuerza", [markdown(NB05_INTRO)]),
        ("from src.visualization import animate_muscle_contraction", [code(NB05_FLOW_CODE)]),
        ("force_table = pd.DataFrame", [markdown(NB05_CONVERSION), markdown(NB05_METRICS)]),
    ],
    "06_project_summary.ipynb": [
        ("# Simulación progresiva", [markdown(NB06_INTRO)]),
        ("fig.tight_layout(); plt.show()", [markdown(NB06_RESULTS)]),
    ],
}


def enrich_notebook(path, rules):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    original = [cell for cell in notebook["cells"] if cell.get("metadata", {}).get("explanation_pack") != TAG]
    pending = list(rules)
    enriched = []
    for cell in original:
        enriched.append(cell)
        source = "".join(cell.get("source", []))
        matched = []
        for index, (anchor, additions) in enumerate(pending):
            if anchor in source:
                enriched.extend(additions)
                matched.append(index)
        for index in reversed(matched):
            pending.pop(index)
    if pending:
        missing = ", ".join(anchor for anchor, _ in pending)
        raise RuntimeError(f"Missing insertion anchors in {path.name}: {missing}")
    notebook["cells"] = enriched
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def enrich_all():
    for name, rules in PACKS.items():
        enrich_notebook(NOTEBOOKS / name, rules)
        print(f"Enriched {name}")


if __name__ == "__main__":
    enrich_all()

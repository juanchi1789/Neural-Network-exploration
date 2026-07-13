# Theoretical Background

## Modelo de Izhikevich

El modelo combina una variable rápida de potencial de membrana `v` con una variable lenta de recuperación `u`:

```text
dv/dt = 0.04v² + 5v + 140 - u + I
du/dt = a(bv - u)
```

Cuando `v >= 30 mV` se registra un spike y se aplica `v = c`, `u = u + d`. Los parámetros `a` y `b` controlan la recuperación; `c` y `d`, el reset. Su bajo número de variables permite simular pools pequeños con un costo reducido. Los presets usados aquí representan patrones funcionales y no calibraciones celulares específicas.

## Motoneuronas

Las motoneuronas constituyen la salida neuronal hacia el músculo. En este proyecto se representan mediante el preset *Regular Spiking*, reciben un comando motor común, ruido individual y heterogeneidad de parámetros. El modelo no incluye tamaño de unidad motora, axón, placa neuromuscular ni reclutamiento fisiológico.

## Spikes y Fuerza Muscular

Cada spike genera una respuesta contráctil elemental o twitch. Se utiliza una diferencia de exponenciales porque produce una subida rápida seguida de una relajación más lenta. La matriz de spikes se suma entre motoneuronas para formar impulsos poblacionales y se convoluciona con el kernel twitch. La superposición temporal de respuestas genera la fuerza total en unidades arbitrarias.

## Inhibición Recurrente

Las motoneuronas excitan un pool pequeño de células de Renshaw mediante `W_MN_to_R`. Las Renshaw devuelven una corriente inhibitoria mediante `W_R_to_MN`, que se resta del input motor. Ambas matrices guardan magnitudes positivas con filas como origen y columnas como destino. El preset *Fast Spiking* de las Renshaw es una aproximación funcional.

## Inhibición Recíproca

La inhibición recíproca y el sistema agonista–antagonista no están implementados en la versión actual. Permanecen como extensión futura para estudiar fuerza neta y coordinación entre pools opuestos.

## Limitaciones del Modelo

Las conexiones son aleatorias, el input es artificial, los parámetros no están calibrados con datos experimentales y las sinapsis no incluyen conductancias, retardos ni plasticidad. No existe feedback sensorial, músculo antagonista ni biomecánica. Los resultados describen el comportamiento cualitativo de este modelo y esta parametrización.

# Project Flow

Este archivo resume el pipeline conceptual del proyecto y sirve como guía rápida para conectar las fases de implementación.

## Flujo Principal

```mermaid
flowchart TD
    A[Input / Motor Command] --> B[Izhikevich Neuron]
    B --> C[Motor Neuron Pool]
    C --> D[Spikes]
    D --> E[Muscle Twitch Model]
    E --> F[Muscle Force]
    F --> G[Visual Muscle Contraction]
```

## Flujo Extendido

```mermaid
flowchart TD
    A[Motor Command] --> B[Motor Neuron Pool]
    B --> C[Renshaw-like Recurrent Inhibition]
    C --> D[Regulated Motor Output]
    D --> E[Muscle Force]
    E --> F[Agonist / Antagonist System]
    F --> G[Net Force / Movement Proxy]
```

## Lectura por Fases

- **Fase 1:** una neurona Izhikevich permite validar la dinámica spiking básica.
- **Fase 2:** distintos inputs permiten estudiar sensibilidad y patrones de disparo.
- **Fase 3:** un pool motor introduce actividad poblacional.
- **Fase 4:** los spikes se transforman en una fuerza muscular simplificada.
- **Fase 5:** la inhibición recurrente regula la salida motora.
- **Fase 6:** el sistema agonista-antagonista permite calcular fuerza neta o proxy de movimiento.
- **Fase 7:** la visualización traduce la simulación a una demo interpretable.


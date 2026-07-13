# Resumen de Trabajo Final

## Simulación progresiva de un circuito neuromotor mediante neuronas de Izhikevich

## 1. Introducción

Este trabajo desarrolla una simulación computacional progresiva de un circuito neuromotor simplificado. El recorrido comienza con una neurona individual, continúa con pools neuronales y redes conectadas, incorpora un circuito de inhibición recurrente tipo Renshaw y finaliza con la transformación de los spikes de las motoneuronas en una señal muscular estimada.

El propósito no es reproducir de manera completa la fisiología del sistema motor ni construir un modelo biomecánico. Se busca una implementación pequeña, reproducible, visual e interpretable que permita comprender cómo se conectan distintos niveles de una simulación neuromotora:

```text
Input externo
      ↓
Dinámica de una neurona spiking
      ↓
Actividad de un pool neuronal
      ↓
Conectividad sináptica
      ↓
Feedback inhibitorio tipo Renshaw
      ↓
Conversión de spikes en activación muscular simplificada
```

## 2. Objetivo general

Construir un modelo computacional progresivo que vincule la actividad de neuronas spiking con un circuito de inhibición recurrente y una salida muscular simplificada, priorizando claridad conceptual, modularidad y reproducibilidad.

## 3. Objetivos específicos

- Implementar el modelo neuronal de Izhikevich

- Explorar diferentes formas de corriente externa o comando motor

- Simular una neurona individual y un pool neuronal heterogéneo

- Representar conexiones sinápticas mediante matrices de pesos

- Incorporar conexiones excitatorias e inhibitorias con dinámica temporal

- Construir un circuito con motoneuronas y células de Renshaw idealizadas

- Comparar configuraciones manteniendo controladas las fuentes de aleatoriedad

- Convertir los spikes de las motoneuronas en una señal contráctil basada en twitches

## 4. Alcance del modelo

El trabajo se plantea como una maqueta computacional. Las neuronas, sinapsis, conexiones y respuestas musculares utilizan unidades y parámetros abstractos o idealizados. El circuito permite estudiar relaciones funcionales entre sus componentes, pero no pretende estimar directamente voltajes, corrientes o fuerzas de un sistema biológico real.

Las principales simplificaciones metodológicas son:

- parámetros neuronales no calibrados con registros experimentales específicos
- conexiones aleatorias
- comando motor artificial
- sinapsis basadas en corriente y estados exponenciales
- ausencia de retardos axonales, plasticidad y potenciales de reversión
- ausencia de feedback sensorial
- ausencia de músculo antagonista y biomecánica articular
- fuerza muscular expresada en unidades arbitrarias

## 5. Modelo neuronal

### 5.1. Ecuaciones de Izhikevich

La dinámica neuronal se representa mediante:

$
\frac{dv}{dt}=0.04v^2+5v+140-u+I
$

$
\frac{du}{dt}=a(bv-u)
$

donde:

- `v` es el potencial de membrana;
- `u` es una variable de recuperación;
- `I` es la corriente total recibida;
- `a` controla la velocidad de recuperación;
- `b` controla el acoplamiento entre `v` y `u`;
- `c` es el potencial aplicado después de un spike;
- `d` es el incremento de recuperación después del spike.

Cuando `v` alcanza 30 mV se registra un spike y se aplica:

$
v=c,\qquad u=u+d
$

La elección de este modelo permite representar diferentes patrones de disparo con pocas variables y un costo computacional reducido.


## 6. Generación de inputs

Se implementaron distintas formas de corriente externa para estudiar cómo cambia la actividad neuronal frente a comandos temporales diferentes:

- corriente constante
- pulso
- rampa
- señal sinusoidal
- comando motor artificial con subida, mantenimiento y relajación
- ruido individual

El input se genera como un vector alineado con el tiempo de simulación. En los pools neuronales puede compartirse una señal común y agregarse ruido independiente a cada neurona.

## 7. Pool neuronal y heterogeneidad

El modelo individual se extendió a poblaciones pequeñas. Cada neurona conserva sus propias variables `v` y `u`, por lo que las matrices de estado tienen la forma:

```text
(número de neuronas, número de pasos temporales)
```

La heterogeneidad se introduce mediante pequeñas variaciones aleatorias en `a`, `b`, `c` y `d`. Esto evita que todas las neuronas respondan de manera idéntica al mismo comando motor.

### 7.1. Semilla aleatoria

La semilla controla el generador pseudoaleatorio empleado para producir:

- variaciones de parámetros;
- ruido de input;
- máscaras de conectividad.

No es una propiedad biológica. Su función es metodológica:

```text
misma configuración + misma semilla → misma realización

misma configuración + otra semilla  → nueva realización aleatoria
```

Fijar la semilla permite reproducir una simulación y comparar escenarios sin cambiar simultáneamente el ruido o la conectividad. Repetir un experimento con varias semillas permite evaluar la robustez del procedimiento.

## 8. Conectividad sináptica

### 8.1. Matriz de pesos

Las conexiones entre neuronas se representan mediante una matriz `W` con la convención:

```text
W[i, j] = efecto de la neurona origen i sobre una neurona destino j
```

Por lo tanto:

- las filas representan neuronas de origen;
- las columnas representan neuronas de destino;
- un cero indica ausencia de conexión;
- la magnitud indica la fuerza de la conexión;
- el uso o signo del peso determina si la conexión es excitatoria o inhibitoria.

Las matrices se crean mediante máscaras aleatorias controladas por una probabilidad de conexión. La probabilidad define cuántas conexiones existen, mientras que el peso define la magnitud de cada conexión.

## 9. Circuito de inhibición recurrente tipo Renshaw

El circuito utiliza dos poblaciones:

- un pool de motoneuronas
- un pool más pequeño de células de Renshaw.

Las motoneuronas utilizan inicialmente un preset `Regular Spiking`. Las Renshaw utilizan `Fast Spiking` como aproximación funcional a una interneurona rápida. Estos presets no constituyen una calibración biológica específica.

### 9.1. Flujo del circuito

```text
comando motor
      ↓

pool de motoneuronas

      ↓ 

spikes y estados sinápticos W_MN_to_R

      ↓ 

excitación pool de células de Renshaw

      ↓ 

spikes y estados sinápticos W_R_to_MN

      ↓ 

corriente inhibitoria resta sobre el input de las motoneuronas

      ↓
nueva actualización del pool motor
```

### 9.2. Matrices del circuito

Se emplean dos matrices distintas:

```text
W_MN_to_R:  motoneuronas → Renshaw
W_R_to_MN:  Renshaw → motoneuronas
```

Por ejemplo con 20 motoneuronas y 5 Renshaw:

```text
W_MN_to_R.shape = (20, 5)
W_R_to_MN.shape = (5, 20)
```

Ambas matrices almacenan magnitudes positivas. `W_MN_to_R` se utiliza como excitación. `W_R_to_MN` representa una vía inhibitoria porque su corriente se resta explícitamente del input motor:

$
I_{MN}=I_{motor}+I_{ruido}-I_{Renshaw}
$

$
I_R=I_{MN\rightarrow R}+I_{ruido,R}
$

Esta convención mantiene separado el valor almacenado en la matriz del efecto funcional que produce en la ecuación.

## 10. Diseño de comparaciones

Para estudiar el papel de la inhibición recurrente se definieron escenarios con distintas magnitudes de la vía `Renshaw → motoneurona`.

La metodología mantiene constantes:

- tamaño de los pools
- input externo
- parámetros neuronales base
- nivel de ruido
- probabilidades de conexión

El único parámetro que se modifica entre escenarios es la magnitud inhibitoria.

## 11. Métricas implementadas

Las métricas se utilizan para resumir la actividad sin depender únicamente de una inspección visual:

- spikes totales
- firing rate medio
- cantidad de motoneuronas activas
- actividad poblacional por ventanas temporales
- pico de actividad poblacional
- corriente inhibitoria media
- intervalos entre spikes
- variabilidad de los intervalos
- fuerza máxima
- fuerza media
- tiempo hasta el pico de fuerza

Estas métricas forman parte del método de análisis. Deben interpretarse junto con rasters, potenciales y señales temporales, ya que cada una resume un aspecto diferente de la simulación.

## 12. Conversión de spikes en fuerza muscular

### 12.1. Twitch elemental

Cada spike genera una respuesta contráctil elemental:

$
h(t)=A\left(e^{-t/\tau_{decay}}-e^{-t/\tau_{rise}}\right),\qquad t\geq0
$

Se utiliza esta diferencia de exponenciales porque produce una subida rápida seguida por una relajación más lenta. La condición `tau_decay > tau_rise` mantiene una forma positiva y causal.

Se eligió por su simplicidad, bajo número de parámetros y capacidad para representar sumación temporal sin introducir un modelo muscular complejo.

### 12.2. Convolución de spikes y twitches

La matriz de spikes se suma entre motoneuronas para formar un tren poblacional de impulsos. Luego se convoluciona con el kernel twitch:

$
F[t]=\sum_{k=0}^{t} impulsos[k]h[t-k]
$

El procedimiento completo es:

```text
Matriz de spikes

      ↓ 
Sumar motoneuronas tren poblacional de impulsos

      ↓ 
Aplicar un twitch a cada impulso convolución temporal

      ↓
Suma de twitches superpuestos

      ↓
Fuerza total en unidades arbitrarias
```

La señal obtenida es un proxy de activación muscular. No se calcula fuerza física, torque articular ni movimiento.



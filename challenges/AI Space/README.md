---
challenge: AI Space
type: AI/ML
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ai-ml, embeddings, mds, data-analysis, python]
---

# AI Space — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega coordenadas o embeddings de un espacio latente y pide identificar la muestra que se separa del resto. Se calculan distancias, se reduce la dimensionalidad con MDS/PCA y se localiza el punto anómalo, que contiene la flag.

## Enunciado y superficie

- AI/ML, Easy, retirado.
- Se entrega un CSV/JSON con vectores o una matriz de distancias.
- El enunciado habla de un espacio multidimensional.

```bash
head data.csv
python3 -c 'import pandas as pd; print(pd.read_csv("data.csv").shape)'
```

## Reconocimiento

- Identificar columnas, etiquetas y valores faltantes.
- Normalizar los vectores antes de medir distancias.
- Representar el espacio con PCA o MDS.
- Buscar outliers por distancia al centroide o vecinos.

## Análisis de los datos

```python
import pandas as pd
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data.csv')
X = StandardScaler().fit_transform(df.select_dtypes('number'))
coords = MDS(n_components=2, random_state=0).fit_transform(X)
```

Al proyectar, una muestra queda fuera del grupo principal. Su índice o etiqueta corresponde al candidato que contiene la flag.

## Explicación del fallo

La flag no está oculta criptográficamente: está codificada en una muestra que rompe la distribución. El reto evalúa si se sabe medir similitud y visualizar un espacio de embeddings sin sobreajustar.

## Reproducción local

```bash
python3 -m pip install pandas scikit-learn matplotlib
python3 analysis.py
```

## Explotación

Se calcula la distancia de cada punto al centroide, se ordenan y se revisa el más alejado. Si la etiqueta es un texto, se decodifica; si es una imagen, se abre la muestra correspondiente.

## Evidencia

- Matriz cargada y normalizada.
- Gráfico MDS/PCA con el outlier.
- Índice/etiqueta de la muestra.
- Flag redactada.

## Lecciones aprendidas

- Normalizar es clave antes de medir distancias.
- MDS conserva distancias, PCA conserva varianza.
- Un outlier puede ser ruido o la respuesta.

## Mitigaciones y detección

- Validar y limpiar embeddings antes de usarlos.
- No asumir que una proyección 2D conserva toda la estructura.
- Documentar el preprocesamiento.
- Referencias: scikit-learn MDS, HTB AI Space, OWASP AI.

## Referencias

- <https://www.hackthebox.com/challenges/AI%20Space>
- <https://www.1337sheets.com/p/hack-the-box-challenge-ai-space-ml-writeup>
- <https://scikit-learn.org/stable/modules/manifold.html#multidimensional-scaling>
- <https://owasp.org/www-project-ai-security-and-privacy-guide/>

---
challenge: AI Space
type: AI/ML
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ai-ml, embeddings, mds, data-analysis, python]
---

# AI Space — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides coordinates or embeddings from a latent space and asks for the sample separated from the rest. Compute distances, reduce dimensionality with MDS/PCA and locate the anomalous point that contains the flag.

## Statement and surface

- AI/ML, Easy, retired.
- A CSV/JSON with vectors or a distance matrix is provided.
- The prompt mentions a multidimensional space.

```bash
head data.csv
python3 -c 'import pandas as pd; print(pd.read_csv("data.csv").shape)'
```

## Reconnaissance

- Identify columns, labels and missing values.
- Normalize vectors before measuring distances.
- Project the space with PCA or MDS.
- Look for outliers by centroid or neighbor distance.

## Data analysis

```python
import pandas as pd
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data.csv')
X = StandardScaler().fit_transform(df.select_dtypes('number'))
coords = MDS(n_components=2, random_state=0).fit_transform(X)
```

After projection, one sample falls outside the main cluster. Its index or label is the candidate containing the flag.

## Flaw explanation

The flag is not cryptographically hidden: it is encoded in a sample that breaks the distribution. The challenge tests similarity measurement and embedding visualization without overfitting.

## Local reproduction

```bash
python3 -m pip install pandas scikit-learn matplotlib
python3 analysis.py
```

## Exploitation

Compute each point's distance to the centroid, sort and inspect the farthest. If the label is text, decode it; if it is an image, open the matching sample.

## Evidence

- Loaded and normalized matrix.
- MDS/PCA plot with the outlier.
- Sample index/label.
- Flag redacted.

## Lessons learned

- Normalization matters before distance measurement.
- MDS preserves distances; PCA preserves variance.
- An outlier can be noise or the answer.

## Mitigations and detection

- Validate and clean embeddings before use.
- Do not assume a 2D projection preserves all structure.
- Document preprocessing.
- References: scikit-learn MDS, HTB AI Space, OWASP AI.

## References

- <https://www.hackthebox.com/challenges/AI%20Space>
- <https://www.1337sheets.com/p/hack-the-box-challenge-ai-space-ml-writeup>
- <https://scikit-learn.org/stable/modules/manifold.html#multidimensional-scaling>
- <https://owasp.org/www-project-ai-security-and-privacy-guide/>

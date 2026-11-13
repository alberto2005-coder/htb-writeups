---
challenge: Sigma Technology
type: AI/ML
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ai, adversarial-ml, tensorflow, image-classification, evasion]
---

# Sigma Technology — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An image classifier accepts five modified pixels on a 32×32 dog image. The goal is to force a misclassification into a non-animal class. The flaw is adversarial machine learning: small, user-controlled perturbations change the prediction.

## Prompt and surface

- AI/ML category, Easy difficulty, retired.
- `sigmanet.h5` and `model.py` are provided.
- A web page lets the player choose the position and RGB colour of five pixels.
- The model predicts ten classes (airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck).

```bash
curl -s -I http://<HOST>:<PORT>/
```

## Reconnaissance

- The base image is a 32×32 dog.
- The model and inference code let the player reproduce predictions locally.
- The page returns only the label and confidence; weights and gradients are not exposed.

```python
import imageio, numpy as np
img = np.array(imageio.imread("dog.png", pilmode="RGB"))
print(img.shape)
```

## Analysis

1. Load the model and confirm it reproduces the original label.
2. Generate five random positions and colours.
3. Score confidence for non-animal classes.
4. Keep the best candidates and mutate one position or channel.
5. Repeat until the prediction is `airplane`, `automobile`, `ship` or `truck`.
6. Submit the five pixels to the remote instance.

```python
pred, conf = sigmanet.predict_one(modified_image)
score = max(conf[0][0], conf[0][1], conf[0][8], conf[0][9])
```

## Root cause

The model accepts user-controlled input and the application trusts its prediction without checking similarity to the original image. A five-pixel perturbation is enough to cross a decision boundary.

This is not memory corruption or injection: it is a lack of robustness to adversarial examples.

## Local reproduction

```bash
python3 -m venv venv
. venv/bin/activate
pip install tensorflow pillow numpy imageio
python3 solve.py
```

The script keeps several candidates, mutates one variable per iteration and sorts by confidence. The search is stochastic; set a seed for repeatability.

## Evidence

- Original prediction and confidence.
- Five modified pixels and the new label.
- Instance response, with the flag redacted.

## Lessons learned

- Model accuracy does not imply robustness.
- Limiting the number of pixels does not remove risk when the user chooses them.
- Random search guided by confidence is enough for this model.

## Mitigations and detection

- Validate that input remains similar to the original.
- Train with adversarial examples and restrict allowed changes.
- Do not use the prediction as the sole security decision.
- Log anomalous inputs and unusual confidences.

## References

- <https://www.hackthebox.com/challenges/267>
- <https://owasp.org/www-project-machine-learning-security-top-10/>
- <https://attack.mitre.org/techniques/T1548/>

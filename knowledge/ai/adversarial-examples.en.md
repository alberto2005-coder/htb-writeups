---
topic: Adversarial examples
tags: [ai, machine-learning, evasion, robustness, image-classification]
---

# Adversarial examples

**English** | [🇪🇸 Español](adversarial-examples.md)

## Concept

An adversarial example is an input deliberately modified so a machine-learning model produces an incorrect prediction. The perturbation may be invisible or limited to a few pixels, but it exploits the decision boundary learned by the model.

This is not memory corruption or injection: it is a lack of robustness to out-of-distribution inputs.

## When it applies

- Image, text or audio classifiers exposed to users.
- Systems accepting attacker-controlled files or parameters.
- Models used for access control, moderation or detection.
- Challenges allowing a limited number of values to be changed.

## Requirements and conditions

- Access to the model or an API returning label and confidence.
- Ability to modify the input within a budget.
- Knowledge of the classes and input format.
- Often a known model (white-box); sometimes only the output (black-box).

## Procedure

1. Reproduce the original prediction and measure confidence.
2. Define an objective: maximise confidence for a wrong class.
3. Generate random perturbations within the allowed budget.
4. Keep the best candidates and mutate one variable at a time.
5. Validate locally before sending to the API.
6. Confirm the label changed and the input is still valid.

```python
pred, conf = model.predict_one(image)
score = max(conf[0][target_classes])
```

White-box attacks can use gradients (FGSM, PGD). Black-box attacks use random search, evolutionary optimisation or transfer attacks from a substitute model.

## Variants

- **FGSM:** one perturbation along the gradient.
- **PGD:** iterative FGSM with projection onto the budget.
- **Adversarial patch:** modifies a specific image region.
- **Data poisoning:** alters training, not just inference.
- **Prompt injection:** the language-model equivalent, with instructions in the input.

## Limitations

- The perturbation may not transfer between models.
- Applications often limit the number of changes.
- Confidence does not always reflect robustness.
- A working example may fail after retraining.

## Mitigation

- Train with adversarial examples.
- Validate similarity to the original input.
- Limit the number and magnitude of allowed changes.
- Use ensembles and anomaly detection.
- Do not base a security decision solely on the prediction.

## Detection

- Log inputs with anomalous confidence or minimal changes.
- Compare input with the original and expected distribution.
- Alert on repeated probing patterns from one account.
- Monitor queries that maximise specific classes.

## References

- <https://owasp.org/www-project-machine-learning-security-top-10/>
- <https://arxiv.org/abs/1412.6572>
- <https://attack.mitre.org/techniques/T1548/>

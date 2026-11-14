---
topic: Abuso de un índice PyPI interno
tags: [linux, pypi, supply-chain, setup.py, python]
---

# Abusing an Internal PyPI Index

**English** | [🇪🇸 Español](pypi-package-abuse.md)

## Concept

A private PyPI index allows packages to be published. If a privileged user installs a controlled package, `setup.py` runs during installation. The chain worsens when `sudo pip` is allowed.

## When it applies

- `pip install` from an unsigned internal index.
- Publishing credentials are accessible.
- `sudo pip` or a service installs packages automatically.

## Procedure

1. Enumerate the index and its credentials.
2. Create a package whose `setup.py` calls back.
3. Publish it with `twine`.
4. Wait for installation or trigger it.
5. Verify which user runs the code.

```bash
python3 -m build
twine upload --repository-url http://<INDEX>/ dist/*
```

## Variants

- Malicious dependency in `install_requires`.
- `post-install` script.
- Typosquatting a legitimate package.

## Limitations

- A signed index or proxy blocks new packages.
- Installation may use an unprivileged user.
- `--no-build-isolation` changes behaviour.

## Mitigation

- Sign packages and verify hashes.
- Restrict publishing and review dependencies.
- Never use `sudo pip`.
- Use virtual environments and internal mirrors.

## Detection

- New packages with obfuscated `setup.py`.
- Outbound connections during `pip install`.
- Installs running as root.

## References

- <https://owasp.org/www-community/attacks/Supply_Chain_Attack>
- <https://attack.mitre.org/techniques/T1546/>
- <https://attack.mitre.org/techniques/T1059/006/>

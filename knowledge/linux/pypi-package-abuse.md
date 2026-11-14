---
topic: Abuso de un índice PyPI interno
tags: [linux, pypi, supply-chain, setup.py, python]
---

# Abuso de un índice PyPI interno

[🐬 English](pypi-package-abuse.en.md) | **Español**

## Concepto

Un índice PyPI privado permite publicar paquetes. Si un usuario con privilegios instala un paquete controlado, `setup.py` se ejecuta durante la instalación. La cadena se agrava si `sudo pip` está permitido.

## Cuándo aplica

- `pip install` desde un índice interno sin firma.
- Credenciales de publicación accesibles.
- `sudo pip` o un servicio que instala paquetes automáticamente.

## Procedimiento

1. Enumerar el índice y sus credenciales.
2. Crear un paquete con `setup.py` que ejecute un callback.
3. Publicarlo con `twine`.
4. Esperar la instalación o forzarla.
5. Verificar el usuario que ejecuta el código.

```bash
python3 -m build
twine upload --repository-url http://<INDEX>/ dist/*
```

## Variantes

- Dependencia maliciosa en `install_requires`.
- `post-install` script.
- Sustitución de un paquete legítimo.

## Limitaciones

- Un índice firmado o un proxy bloquea paquetes nuevos.
- La instalación puede usar un usuario sin privilegios.
- `--no-build-isolation` cambia el comportamiento.

## Mitigación

- Firmar paquetes y verificar hashes.
- Restringir publicación y revisar dependencias.
- Nunca usar `sudo pip`.
- Usar entornos virtuales y réplicas internas.

## Detección

- Paquetes nuevos con `setup.py` ofuscado.
- Conexiones salientes durante `pip install`.
- Instalaciones como root.

## Referencias

- <https://owasp.org/www-community/attacks/Supply_Chain_Attack>
- <https://attack.mitre.org/techniques/T1546/>
- <https://attack.mitre.org/techniques/T1059/006/>

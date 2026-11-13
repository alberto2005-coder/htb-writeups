# HTB Writeups — alberto2005coder

**Español** | [English](README.en.md)

Repositorio personal de writeups, notas técnicas y metodología de **Hack The Box**. El objetivo es documentar el razonamiento, la evidencia y las mitigaciones, no solo los comandos utilizados.

> Las máquinas, retos y Sherlocks activos se mantienen fuera de la publicación. Solo se publican contenidos de laboratorios autorizados y respetando las normas de HTB.

## Contenido

<!-- BEGIN AUTO-GENERATED STATS -->
- **Writeups:** 396 (162 máquinas, 127 retos y 107 Sherlocks; fichas ES/EN).
- **Conocimiento:** 97 temas con fichas ES/EN.
<!-- END AUTO-GENERATED STATS -->

| Sección | Índice |
|---|---|
| Máquinas | [Catálogo](machines/catalog.md) · [Índice automático](machines/INDEX.generated.md) |
| Retos | [Índice curado](challenges/README.md) · [Índice automático](challenges/INDEX.generated.md) |
| Sherlocks | [Índice curado](sherlocks/README.md) · [Índice automático](sherlocks/INDEX.generated.md) |
| Conocimiento | [Índice por temas](knowledge/README.md) · [Índice automático](knowledge/README.md) |
| Plantillas | [Templates](templates/) |
 
## Metodología

1. **Reconocimiento y enumeración:** identificar superficie de ataque y servicios.
2. **Acceso inicial:** documentar vulnerabilidad, hipótesis y evidencia.
3. **Movimiento lateral y escalada:** explicar permisos, rutas y condiciones necesarias.
4. **Validación:** conservar evidencias reproducibles y separar hechos de hipótesis.
5. **Mitigación y detección:** explicar cómo prevenir y detectar la técnica.

## Desarrollo y validación

Requisitos: Git y Python 3.8 o posterior. No se requieren dependencias externas.

```bash
python tools/generate_indexes.py
python tools/repo_check.py
python tools/audit-indices.py
```

Para instalar los hooks locales:

```bash
sh .githooks/install.sh
```

Los índices marcados como generados no deben editarse manualmente. Ejecuta el generador después de añadir o eliminar fichas. CI comprueba que los archivos generados estén actualizados.

## Uso responsable

Todo el contenido se refiere a entornos de laboratorio autorizados. No publiques credenciales, claves privadas, flags reales ni evidencias sensibles. Los writeups de máquinas activas permanecen privados hasta que HTB las retire.

## Licencias

El código fuente y los scripts propios se ofrecen bajo MIT (ver [LICENSE](LICENSE)). La documentación original se ofrece bajo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (ver [LICENSE-DOCS](LICENSE-DOCS)). Los materiales de terceros conservan sus respectivas licencias y atribuciones.

## Perfil

- Hack The Box: [alberto2005coder](https://app.hackthebox.com/users/4187928)
- Áreas de estudio: pentesting web, Linux, Active Directory y cloud.

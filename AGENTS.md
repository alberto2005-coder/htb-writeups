# Instrucciones del proyecto

## Carpetas temporales de lote

- Cada lote usa una carpeta temporal `.tmp_loteNN/` para descargas, texto extraído y scripts de generación.
- Al empezar un lote nuevo, elimina la carpeta `.tmp_loteNN` del lote anterior antes de crear la nueva. No reutilices ni acumules carpetas de lotes anteriores.
- Al cerrar un lote, elimina también su propia carpeta temporal. En cualquier caso, al iniciar el siguiente no debe quedar ninguna carpeta `.tmp_lote*` previa.
- Estas carpetas son material de trabajo, no contenido publicable; no las añadas a Git ni las incluyas en los commits.

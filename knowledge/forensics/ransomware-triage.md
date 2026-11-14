---
topic: Ransomware triage
tags: [forensics, ransomware, encryption, shadow-copies, timeline, recovery]
---

# Ransomware triage

[🌐 English](ransomware-triage.en.md) | **Español**

## Concepto

El triaje de ransomware reconstruye el acceso inicial, la propagación, el cifrado y la nota de rescate. El objetivo inmediato es contener, preservar evidencia y localizar copias limpias; el análisis posterior identifica la familia y el alcance.

## Cuándo aplica

- Archivos cifrados o con extensión nueva.
- Nota de rescate en directorios.
- Shadow copies eliminadas.
- Cuentas o servicios usados para propagarse.

## Procedimiento

1. Aislar los equipos sin apagar la memoria.
2. Preservar nota, binarios y logs.
3. Revisar shadow copies, backups y volumenes.
4. Construir el timeline de cifrado y accesos.
5. Identificar la familia y el alcance.

```powershell
vssadmin list shadows
Get-ChildItem C:\ -Recurse -Filter *.txt -ErrorAction SilentlyContinue | Select-String -Pattern 'ransom|decrypt'
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625} -MaxEvents 100
```

## Variantes

- Ransomware con cifrado rápido y nota.
- Eliminación de shadow copies.
- Propagación por SMB o GPO.
- Doble extorsión con exfiltración previa.

## Limitaciones

- El cifrado puede ser irreversible sin la clave.
- Los logs pueden haberse borrado.
- La nota puede ser genérica o falsa.
- La recuperación depende de backups íntegros.

## Mitigación y detección

- Backups inmutables y probados.
- Segmentación y mínimo privilegio.
- Monitorizar eliminación de shadow copies y cifrado masivo.
- Ensayar respuesta y preservación de evidencia.

## Referencias

- <https://www.cisa.gov/stopransomware>
- <https://attack.mitre.org/techniques/T1486/>
- <https://www.sans.org/white-papers/ransomware-response/>

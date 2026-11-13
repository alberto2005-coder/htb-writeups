---
topic: Sliver C2
tags: [windows, sliver, c2, implant, dfir, network, persistence]
---

# Sliver C2

[🌐 English](sliver-c2.en.md) | **Español**

## Concepto

Sliver es un framework de command and control con implantes para Windows, Linux y macOS. Los implants pueden usar mTLS, HTTPS, DNS o WireGuard, y ejecutar tareas, túneles y movimiento lateral. El análisis busca el binario, la configuración embebida, los canales y los artefactos de ejecución.

## Cuándo aplica

- Tráfico C2 cifrado hacia un dominio o IP.
- Procesos con nombre legítimo pero firma ausente.
- Persistencia y tareas programadas.
- Análisis de memoria o de un binario sospechoso.

## Procedimiento

1. Aislar el host y preservar memoria y disco.
2. Buscar procesos, servicios y tareas anómalas.
3. Extraer cadenas, dominios, certificados y claves.
4. Correlacionar conexiones y beaconing.
5. Identificar el implante y su configuración.

```powershell
Get-Process | Where-Object { $_.Path -and -not (Get-AuthenticodeSignature $_.Path).SignerCertificate }
Get-NetTCPConnection -State Established
Get-ScheduledTask | Where-Object { $_.Actions.Execute -match 'AppData|ProgramData|Temp' }
```

## Variantes

- Implante mTLS con certificado embebido.
- HTTPS con dominio fronting.
- DNS o WireGuard.
- Sesiones interactivas, túneles y ejecución de assemblies.

## Limitaciones

- La configuración puede estar cifrada.
- El binario puede estar ofuscado o empaquetado.
- El C2 puede usar infraestructura legítima.
- Sin memoria, parte del contexto se pierde.

## Mitigación y detección

- Firmar y permitir solo binarios conocidos.
- Monitorizar beaconing, certificados y dominios nuevos.
- Restringir creación de servicios y tareas.
- Alertar de procesos sin firma y conexiones salientes periódicas.

## Referencias

- <https://github.com/BishopFox/sliver>
- <https://attack.mitre.org/techniques/T1071/>
- <https://www.cisa.gov/resources-tools/resources/command-and-control>

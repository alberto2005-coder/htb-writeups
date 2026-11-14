---
sherlock: Dream Job-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre, lazarus, operation-dream-job, iocs]
---

# Dream Job-1 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un analista de inteligencia debe caracterizar la campaña Operation Dream Job y relacionar los indicadores entregados con el grupo Lazarus. El objetivo es pasar de un IOC suelto a TTP y a una evaluación de impacto.

## Evidencias

- `DreamJob1.zip`, protegido con la contraseña habitual.
- `IOCs.txt` con tres líneas: dos dominios/hashes y una dirección de wallet.
- No se entrega memoria, disco ni PCAP.

```bash
unzip DreamJob1.zip
sha256sum IOCs.txt
cat IOCs.txt
```

## Investigación

### 1. Inventario y triaje

Se anotan los tres indicadores y se clasifican por tipo: infraestructura, malware y financiación. La campaña se identifica por el nombre y por el contexto del enunciado, no por el hash.

### 2. Contraste con MITRE ATT&CK

```text
Campaña: Operation Dream Job (C0022)
Grupo: Lazarus Group (G0032)
Tácticas: Reconnaissance, Initial Access, Execution, Persistence
```

Se revisan las técnicas de la campaña y se separan las observadas en la evidencia de las inferidas por el actor. No se atribuye una técnica solo porque el grupo la haya usado en otra operación.

### 3. Artefacto clave

`IOCs.txt` es el único artefacto. Los dominios se consultan en VirusTotal y en la documentación de MITRE; la wallet se marca como infraestructura de pago, no como C2. Se documenta la fecha de consulta y la confianza.

## Conclusiones

- La campaña se atribuye a Lazarus/Operation Dream Job.
- Los dominios son infraestructura de la campaña; los hashes identifican muestras relacionadas.
- La wallet aporta contexto financiero, no ejecución.
- El impacto esperado es espionaje y robo de credenciales en candidatos de defensa/tecnología.

## Lecciones

- Un IOC aislado no prueba atribución; el contexto de campaña sí ayuda.
- Conviene registrar la fuente y la fecha de cada conclusión.
- La inteligencia de actores debe traducirse en detecciones concretas.

## Referencias

- <https://www.hackthebox.com/sherlocks/Dream%20Job-1>
- <https://attack.mitre.org/campaigns/C0022/>
- <https://attack.mitre.org/groups/G0032/>

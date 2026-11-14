---
sherlock: Neural Noel
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, ai, llm, http, prompt-injection, logs]
---

# Neural Noel — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

El soporte automático de Santa usa un chatbot. Se entregan logs HTTP, archivos sospechosos y prompts; hay que determinar si alguien manipuló el asistente o exfiltró datos.

## Evidencias

- Logs de acceso y de aplicación del servicio de IA.
- Archivos subidos o generados por el chatbot.
- No se entrega el modelo ni la clave de API.

```bash
grep -iE 'prompt|chat|completion|upload' access.log
```

## Investigación

### 1. Inventario y triaje

Se separan peticiones normales de las que incluyen instrucciones, archivos o URLs. Los endpoints de chat, carga y herramientas internas son los relevantes.

### 2. Línea temporal

Se ordenan por tiempo y usuario. Se buscan secuencias de prompt injection: instrucciones para ignorar reglas, revelar el sistema o llamar a una herramienta.

```text
Usuario -> prompt malicioso -> respuesta -> solicitud interna -> exfiltración
```

### 3. Artefacto clave

El prompt y la respuesta muestran si el modelo obedeció una instrucción no confiable. El archivo resultante o la URL de destino confirman el impacto.

## Conclusiones

- El chatbot procesó entrada no confiable.
- La inyección de prompt pudo revelar instrucciones o datos.
- Los logs permiten identificar usuario, sesión y destino.
- El diseño debe separar instrucciones de sistema y datos del usuario.

## Lecciones

- Los LLM no distinguen por sí solos instrucciones y contenido.
- Hay que validar herramientas y salidas del modelo.
- Los logs de aplicación son tan importantes como los de red.

## Referencias

- <https://www.hackthebox.com/sherlocks/Neural%20Noel>
- <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
- <https://attack.mitre.org/techniques/T1059/>

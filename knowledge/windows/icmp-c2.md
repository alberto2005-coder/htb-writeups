---
topic: Windows — canal C2 sobre ICMP
tags: [windows, icmp, c2, tunneling, egress]
---

# Windows — canal C2 sobre ICMP

[🌐 English](icmp-c2.en.md) | **Español**

## Concepto

ICMP suele estar permitido aunque HTTP salga filtrado. Un cliente y un servidor pueden encapsular comandos y salida en paquetes echo request/reply para mantener un canal de control.

## Cuándo aplica

- Egress ICMP permitido y HTTP restringido.
- Host Windows con `ping.exe` o PowerShell.
- Redes planas sin inspección de ICMP.

## Procedimiento

1. Preparar un listener ICMP en el atacante.
2. Ejecutar el cliente en la víctima.
3. Enviar comandos y recibir la salida.
4. Codificar los datos para evitar filtros.
5. Mantener el canal con keepalives.

## Comandos

```powershell
ping -n 1 <ATACANTE>
# Cliente ICMP: encapsula la salida en el payload del echo
```

## Variantes

- Túneles DNS/ICMP combinados.
- PowerShell con `New-Object System.Net.NetworkInformation.Ping`.
- ICMPv6.

## Limitaciones

- ICMP puede estar bloqueado en el firewall.
- El tamaño del payload es limitado.
- Los IDS detectan patrones anómalos.

## Mitigación

- Bloquear ICMP saliente no necesario.
- Inspeccionar y limitar el tamaño de los paquetes.
- Segmentar la red y monitorizar egress.

## Detección

- Echo requests con payloads grandes o repetitivos.
- Tráfico ICMP hacia hosts externos no inventariados.

## Referencias

- <https://attack.mitre.org/techniques/T1095/>
- <https://github.com/bdamele/icmpsh>

---
sherlock: CafePoisoning
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, arp-poisoning, dns-spoofing, pcap, persistence, screensaver, malware]
---

# CafePoisoning — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

La red de una cafetería empieza a redirigir a los clientes a una página de actualización falsa. Se entregan una captura de red y una colección de triaje KAPE de la máquina de un empleado. Hay que reconstruir el ataque, la persistencia y el canal de C2.

## Evidencias

- `cafe.pcap` con tráfico ARP, DNS y HTTP.
- `KAPE/` con registry, prefetch, MFT, navegador y archivos del usuario.
- No se proporciona memoria.

```bash
capinfos cafe.pcap
find KAPE -maxdepth 2 -type d | sort
```

## Investigación

### 1. Inventario y triaje

Se revisan los protocolos de la captura. Hay una ráfaga de ARP requests y respuestas duplicadas: un host intenta asociar la IP del gateway a su propia MAC.

```bash
tshark -r cafe.pcap -Y arp -T fields -e arp.opcode -e arp.src.proto_ipv4 -e arp.src.hw_mac | sort | uniq -c
```

El número de hosts y de respuestas ARP duplicadas delimita el alcance del envenenamiento.

### 2. Envenenamiento y redirección

Tras el ARP spoofing, el tráfico DNS del cliente se dirige al atacante. Las respuestas falsas resuelven un dominio de actualización a una IP controlada.

```bash
tshark -r cafe.pcap -Y 'dns.flags.response == 0' -T fields -e dns.qry.name | sort | uniq -c
tshark -r cafe.pcap -Y 'dns.flags.response == 1' -T fields -e dns.qry.name -e dns.a
```

El dominio imita al fabricante del software. El cliente descarga un ejecutable desde una URL HTTP.

### 3. Ejecución y persistencia

En el triaje se revisan Prefetch, Amcache y el registro. El ejecutable se lanza desde una carpeta de actualizaciones y crea una entrada `Run` que apunta a un screensaver `.scr`.

```bash
PECmd.exe -d KAPE/C -o out --csv out
RegistryExplorer.exe KAPE/C/Windows/System32/config/SOFTWARE
```

La clave `...\CurrentVersion\Run` contiene una ruta de screensaver en `AppData`. El mecanismo es persistencia por ejecución automática.

### 4. Defensas y C2

El instalador ejecuta PowerShell para desactivar Defender y añadir exclusiones. El tráfico posterior al C2 está ofuscado con XOR de un byte; la captura permite recuperar la clave probando los 256 valores y buscando cadenas conocidas.

```bash
python3 - <<'PY'
data = open("c2.bin", "rb").read()
for k in range(256):
    out = bytes(b ^ k for b in data)
    if b"http" in out or b"cmd" in out:
        print(k, out[:120])
PY
```

## Conclusiones

- El acceso inicial fue ARP/DNS poisoning en una red Wi-Fi compartida.
- El usuario descargó un falso actualizador desde un dominio suplantado.
- La persistencia usa una entrada `Run` con un `.scr`.
- El malware desactiva Defender y usa XOR de un byte para el C2.

## Lecciones

- Las redes abiertas permiten ataques de capa 2.
- Un dominio parecido no garantiza legitimidad; verificar firma y origen.
- Las entradas `Run` que apuntan a `AppData` son sospechosas.
- XOR de un byte es ofuscación, no cifrado.

## Referencias

- <https://www.hackthebox.com/sherlocks/CafePoisoning>
- <https://attack.mitre.org/techniques/T1557/002/>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://attack.mitre.org/techniques/T1562/001/>

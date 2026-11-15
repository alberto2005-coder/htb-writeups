---
machine: Chainsaw
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, solidity, blockchain, ipfs, suid, slack-space]
---

# Chainsaw — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El FTP anónimo publica un contrato Solidity y su ABI; el puerto `9810` es un nodo Ethereum. Se interactúa con el contrato y su función `setDomain` ejecuta comandos, lo que da una shell. En IPFS aparece una clave SSH para `bobby`, protegida por una frase que se crackea. Un binario SUID permite obtener root, pero la flag está oculta en el slack space de `root.txt` y se recupera con `bmap` o `debugfs`.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,9810 <IP>
```

- `21/tcp` vsftpd con login anónimo y `22/tcp` OpenSSH.
- `9810/tcp` responde como un nodo JSON-RPC de Ethereum.
- El FTP contiene `WeaponizedPing.json`, `WeaponizedPing.sol` y `address.txt`.

## Enumeración

- El contrato expone `setDomain(string)` y se conecta con `web3.py` al nodo.
- La función pasa el dominio a un comando del sistema sin sanear.
- Los archivos de IPFS incluyen una clave privada SSH para `bobby` y una nota con la frase de paso.

## Foothold

Se despliega o reutiliza el contrato y se llama a `setDomain` con un payload que lanza una reverse shell. La shell cae como el usuario que ejecuta el nodo.

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://<IP>:9810'))
# cargar ABI y dirección, enviar setDomain('; bash -c "..."')
```

Después se descarga la clave de IPFS, se crackea su frase con `john` y se entra como `bobby`.

## Movimiento lateral

No hay otro host. El movimiento es del contrato al sistema, de ahí a `bobby` con la clave SSH y después al binario privilegiado.

## Escalada de privilegios

`bobby` puede ejecutar un binario SUID que interactúa con la imagen del disco. Se usa para montar o leer el sistema como root. La flag no está en el contenido normal de `root.txt`, sino en su slack space.

```bash
find / -perm -4000 -type f 2>/dev/null
bmap --mode checkslack /root/root.txt
bmap --mode slack /root/root.txt
# o con debugfs sobre /dev/sda2
```

## Evidencia

- Contrato y ABI descargados por FTP anónimo.
- `setDomain` con ejecución de comandos y shell inicial.
- Clave de `bobby` y flag leída del slack space.

## Lecciones aprendidas

- Los contratos inteligentes pueden ser una interfaz para comandos del sistema.
- IPFS y FTP anónimos pueden filtrar claves y material sensible.
- La evidencia puede estar en slack space y requerir herramientas forenses.

## Mitigación y detección

- No ejecutar contratos con acceso al shell del host.
- Restringir FTP/IPFS y rotar claves expuestas.
- Auditar binarios SUID y el acceso a dispositivos de bloque.

## Referencias

- [0xdf — Chainsaw](https://0xdf.gitlab.io/2019/11/23/htb-chainsaw.html)
- [IppSec — Chainsaw](https://www.youtube.com/watch?v=vESegBSrm_U)
- [Hack The Box — Chainsaw](https://app.hackthebox.com/machines/chainsaw)

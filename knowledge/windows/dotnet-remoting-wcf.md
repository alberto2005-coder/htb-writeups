---
topic: .NET Remoting y WCF — deserialización y endpoints
tags: [windows, dotnet, remoting, wcf, ysoserial]
---

# .NET Remoting y WCF — deserialización y endpoints

[🌐 English](dotnet-remoting-wcf.en.md) | **Español**

## Concepto

.NET Remoting con `BinaryFormatter` deserializa objetos del canal y permite ejecutar gadgets. WCF puede exponer endpoints con operaciones privilegiadas que ejecutan PowerShell o comandos. La combinación típica es: deserialización para el primer usuario y un endpoint WCF mal protegido para SYSTEM.

## Cuándo aplica

- Hay un servicio .NET Remoting con formateador binario.
- WCF expone un endpoint de administración o ejecución.
- Se puede alcanzar el puerto desde la red interna.

## Procedimiento

1. Enumerar servicios y canales .NET.
2. Generar el gadget con `ysoserial.net`.
3. Enviarlo al canal remoto y obtener una shell.
4. Decompilar el servicio WCF y localizar el endpoint privilegiado.

## Comandos

```bash
nmap -Pn -sCV -p135,445,5985 <IP>
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "calc" -o raw > payload.bin
python3 remoting_client.py <IP> payload.bin
dnSpy.exe <SERVICE>.exe
# Endpoint WCF
python3 wcf_client.py --host <HOST> --command whoami
```

## Variantes

- Usar `ObjectDataProvider` o `WindowsIdentity` como gadget.
- Aprovechar un endpoint WCF con `NetTcpBinding` sin autenticación.
- Encadenar con robo de credenciales del servicio.

## Limitaciones

- El gadget debe estar disponible en el servidor.
- WCF puede exigir autenticación.
- El firewall puede limitar el canal.

## Mitigación

- Eliminar .NET Remoting y `BinaryFormatter`.
- Autenticar y autorizar cada endpoint WCF.
- Ejecutar servicios con cuentas de bajo privilegio.

## Detección

- Tráfico binario .NET Remoting desde hosts no habituales.
- Procesos hijos del servicio WCF.
- Endpoints WCF publicados sin autenticación.

## Referencias

- [ysoserial.net](https://github.com/pwntester/ysoserial.net)
- [0xdf — Sharp](https://0xdf.gitlab.io/2021/05/01/htb-sharp.html)
- [Microsoft — WCF security](https://learn.microsoft.com/en-us/dotnet/framework/wcf/security-in-wcf)

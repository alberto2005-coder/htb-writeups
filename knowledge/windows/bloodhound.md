---
topic: BloodHound
tags: [windows, active-directory, bloodhound, sharphound, acl, attack-path]
---

# BloodHound

[🌐 English](bloodhound.en.md) | **Español**

## Concepto

BloodHound modela usuarios, grupos, equipos, sesiones y ACL de Active Directory como un grafo. Permite encontrar rutas de privilegio —Kerberoasting, delegación, ESC, `GenericAll`, `WriteDacl`— y priorizar el movimiento lateral.

## Cuándo aplica

- Dominio Active Directory enumerable.
- Credenciales de usuario o equipo.
- Búsqueda de rutas a Domain Admin.
- Análisis de ACL y sesiones.

## Procedimiento

1. Recopilar datos con SharpHound o `bloodhound-python`.
2. Importar el ZIP en BloodHound.
3. Revisar usuarios con sesiones privilegiadas.
4. Buscar rutas a Domain Admin.
5. Validar los permisos antes de explotar.

```bash
bloodhound-python -u <USER> -p '<PASSWORD>' -ns <DC> -d <DOMAIN> -c All
# Importar el ZIP en la interfaz de BloodHound
```

## Variantes

- Colector `All` o `DCOnly`.
- Análisis de ACL, delegación y GPO.
- Sesiones y credenciales en equipos.
- Rutas hacia ADCS y cuentas de servicio.

## Limitaciones

- La recolección puede generar mucho ruido.
- Los datos pueden estar incompletos.
- Una ruta visible no siempre es explotable.
- La versión del colector debe coincidir.

## Mitigación y detección

- Auditar ACL y sesiones privilegiadas.
- Aplicar tiering y estaciones PAW.
- Monitorizar consultas LDAP masivas.
- Corregir rutas y permisos innecesarios.

## Referencias

- <https://bloodhound.readthedocs.io/>
- <https://github.com/dirkjanm/BloodHound.py>
- <https://attack.mitre.org/techniques/T1087/002/>

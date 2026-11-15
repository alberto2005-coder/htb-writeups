---
machine: Blurry
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, clearml, pickle, pytorch, deserialization]
---

# Blurry — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ClearML is vulnerable to pickle artifact deserialization (CVE-2024-24590) and yields a shell. Escalation uses a PyTorch evaluator run as root: a malicious `.pth` executes on import and bypasses Fickling detection.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
curl -s http://blurry.htb/ | head
# Malicious pickle artifact uploaded to ClearML
python3 clearml_pickle.py --url http://blurry.htb:8080
# PyTorch evaluator
sudo -l
find / -name "*.pth" 2>/dev/null
```

## Enumeration

- ClearML panel with open registration and sample projects.
- Artifacts and models uploaded by the application.
- A model evaluation script runs periodically as root.

## Initial access

Create a task and upload a malicious pickle artifact. When ClearML retrieves and deserializes it, the payload runs and returns a shell as the application user.

## Privilege escalation

The evaluator loads PyTorch models with `torch.load`. A `.pth` file with code in `runpy` executes during import; Fickling does not flag it and the process runs as root.

## Evidence

- Pickle artifact executed by ClearML.
- Shell as the service user.
- `.pth` model loaded by the root evaluator.

## Lessons learned

- Pickle is code, not a safe data format.
- Detection tools have bypasses; isolation matters more.
- A root model evaluator turns an artifact into privileged execution.

## Mitigation and detection

- Do not deserialize artifacts from untrusted users.
- Run ClearML and evaluators unprivileged, in ephemeral containers.
- Sign models and use safe formats such as Safetensors.

## References

- [0xdf — Blurry](https://0xdf.gitlab.io/2024/10/12/htb-blurry.html)
- [NVD — CVE-2024-24590](https://nvd.nist.gov/vuln/detail/CVE-2024-24590)
- [Hack The Box — Blurry](https://app.hackthebox.com/machines/blurry)

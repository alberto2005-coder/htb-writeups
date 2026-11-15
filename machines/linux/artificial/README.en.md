---
machine: Artificial
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, tensorflow, keras, deserialization, backrest]
---

# Artificial — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The application loads TensorFlow models to make predictions. An `.h5` model with a malicious Lambda layer is deserialized on the server and yields code execution in the container; a Backrest backup exposes credentials and allows hooks to run as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://<IP>/ -H "Host: FUZZ.artificial.htb" -w subdomains.txt
curl -s http://app.artificial.htb/ | head
# Upload a model with a malicious Lambda layer
curl -F "model=@malicious.h5" http://app.artificial.htb/upload
# After access
restic snapshots -r <REPO>
sudo -l
```

## Enumeration

- The main site is a landing page; the real flow lives on an application vhost.
- Model upload accepts `.h5` files and returns the prediction result.
- The container stores a Backrest backup and the database configuration.

## Initial access

`tf.keras.models.load_model` does not treat the file as inert data: rebuilding a `Lambda` layer runs the serialized function. Upload a model whose Lambda starts a reverse shell and obtain a session as the service user.

## Privilege escalation

The backup contains the Backrest configuration and reusable credentials. With SSH access, inspect the service; Backrest runs as root and allows backup hooks, which execute with its privileges.

## Evidence

- Upload response with the prediction and TensorFlow errors.
- Shell in the container after loading the model.
- Backrest hook executed as root.

## Lessons learned

- ML model formats can contain executable code.
- A backup is not just data: it includes secrets and service configuration.
- Hooks of privileged backup services are a direct path to root.

## Mitigation and detection

- Load models with `safe_mode=True` or in an isolated environment without secrets.
- Sign and validate artifacts before deserializing them.
- Run Backrest without root and restrict its hooks.

## References

- [0xdf — Artificial](https://0xdf.gitlab.io/2025/10/25/htb-artificial.html)
- [Hack The Box — Artificial](https://app.hackthebox.com/machines/artificial)
- [TensorFlow — Security](https://www.tensorflow.org/responsible_ai)

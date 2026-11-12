---
challenge: The Suspicious Reviewer
type: OSINT
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [osint, github, email, metadata, profiling]
---

# The Suspicious Reviewer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; not played on this profile.
> The answer is an email address; the **real value is not published**.

## TL;DR

The challenge asks for a reviewer's email from their public profile. The address is in the **About** section and is confirmed by commit metadata. The flag is the email in `HTB{<email>}` format.

## 1. From alias to profile

Start from the name or alias in the prompt. Look for matches on GitHub, GitLab, X/Twitter and a personal blog. Do not settle for the first hit: verify that the activity (reviews, repos, links) matches the described person.

```bash
# Public API, no auth for public profiles
curl -s https://api.github.com/users/<USER> | jq '{login,name,bio,blog,email,created_at}'
```

The `email` field is often `null`; the address may be in the bio, profile README or a `mailto:` link.

## 2. The About section

On the profile, **About** groups bio, location, company, website and socials. Review:

- The bio and profile README (`<USER>/<USER>`).
- The personal site link; look for `Contact`, `About` or the footer.
- Raw HTML, not just rendered text:

```bash
curl -sL https://<PERSONAL_SITE>/ | grep -oiE 'mailto:[^"<> ]+'
curl -sL https://github.com/<USER> | grep -oiE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
```

- `whois` on the personal domain, if it is theirs and not private.
- Published PGP keys: the UID usually contains the email.

## 3. Confirm with commits

Git commits include the author's email. It is a second, independent source:

```bash
git clone --filter=blob:none https://github.com/<USER>/<REPO>.git
git -C <REPO> log --format='%an <%ae>' | sort -u
```

If the commit email matches the About address, the answer is confirmed. Also check releases, patches and `Signed-off-by` lines.

## 4. Rule out decoys

- `noreply@github.com` or `users.noreply.github.com`: not the answer.
- Company or project addresses: may be generic.
- Same-name profiles: compare photo, links and activity.
- Third-party data in the same repository: not the target.

## 5. Answer

Build the flag from the exact address, preserving case and domain:

```text
HTB{<email>}
```

The real value is not included here. In an OSINT challenge the answer is personal information: document the method, not the data.

## Lessons learned

- A public profile's About is the first source, not the only one.
- Git metadata is an independent, hard-to-fake source.
- A `mailto:` in HTML may not appear on the rendered page.
- Distinguish a personal address from the platform's `noreply`.
- Do not publish personal data even when the challenge asks: explain the path, not the result.

## Mitigations (for the analysed profile)

- Use GitHub's `noreply` address in commits.
- Do not publish personal addresses in bio, README or website.
- Review metadata exposed by repositories and PGP keys.
- Separate professional and personal identities.

MITRE: T1593.003, T1589.002.

## References

- <https://thehacksparrow.com/the-suspicious-reviewer/>
- <https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/about-your-profile>
- <https://attack.mitre.org/techniques/T1589/002/>

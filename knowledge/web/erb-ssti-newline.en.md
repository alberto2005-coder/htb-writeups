---
title: ERB SSTI — bypassing the regex with a newline
tags: [web, ruby, erb, ssti, regex, rce]
---

# ERB SSTI — bypassing the regex with a newline

[🇪🇸 Español](erb-ssti-newline.md) | **English**

## Concept

In Ruby, `^` and `$` anchor to the start and end of a **line**, not the string. A validation `params[:x] =~ /^[a-z]+$/` accepts `abc\n<%= ... %>` because the newline satisfies `$` and the rest falls outside the check. If that value is interpolated into an ERB template, it executes.

## When it applies

- The application is Ruby/Sinatra/Rails and uses ERB.
- Input is validated with `^...$` and then concatenated into `ERB.new(...).result(binding)`.
- A newline is allowed in the parameter.

## Procedure

1. Send a valid value followed by `%0a` and `<%= 7*7 %>`.
2. Check whether the response returns `49`.
3. Replace it with `system` or backticks to execute.
4. Encode the reverse shell if filters exist.

```text
category1=Test%0a<%= 7*7 %>
category1=Test%0a<%= system("id") %>
```

```ruby
ERB.new("... #{params[:category1]} ...").result(binding)
```

## Variants

- Use a real `\n` in a JSON body or `%0a` in forms.
- If `system` is blocked, use `IO.popen`, backticks or `eval`.
- In Rails, `render inline:` with user input has the same problem.

## Limitations

- The regex must use `^`/`$`, not `\A`/`\z`.
- The value must reach an ERB template, not an escaped output.
- Word filters may require concatenation.

## Mitigation and detection

- Validate with `\A...\z` and allowlists.
- Never build templates from input; use escaped variables.
- Disable `ERB.new` on untrusted data.
- Search for `%0a`, `<%` and `%>` in parameters and alert.

## References

- <https://ruby-doc.org/stdlib-3.3.0/libdoc/erb/rdoc/ERB.html>
- <https://portswigger.net/web-security/server-side-template-injection>
- <https://owasp.org/www-community/attacks/Code_Injection>

---
topic: ffmpeg — local file read with AVI
tags: [web, ffmpeg, file-read, media, cve]
---

# ffmpeg — local file read with AVI

[🇪🇸 Español](ffmpeg-avi-file-read.md) | **English**

## Concept

ffmpeg processes a wide range of containers and codecs. A crafted AVI can make the demuxer read a local path and include it in an error message, metadata or a frame. If the application converts or thumbnails uploaded files, file read is exposed.

## When it applies

- The panel accepts video and calls ffmpeg to transcode or create thumbnails.
- Error output or the result is returned to the user.
- ffmpeg runs with access to sensitive paths.

## Procedure

1. Identify the version and the ffmpeg command.
2. Create an AVI with a chunk pointing to `/etc/passwd` or a key.
3. Upload it and request the thumbnail or conversion.
4. Read the content in the response or error.

```bash
ffmpeg -f lavfi -i color=c=black:s=32x32 -t 1 -c:v rawvideo -f avi base.avi
# modify the text chunk or filename and upload the result
```

## Variants

- Concatenation lists with `file 'http://...'` or local paths.
- `-vf subtitles=` with a local file.
- Metadata copied into the output file.

## Limitations

- The path must be readable by the ffmpeg user.
- The application must display the error or result.
- A sandbox with `open_basedir` or a container without secrets reduces impact.

## Mitigation

- Run ffmpeg in a container without secrets or network.
- Validate the real file type and restrict codecs.
- Do not return internal errors to users.

## Detection

- ffmpeg processes with paths outside the working directory.
- Demuxer warnings about non-media files.
- CPU spikes from converting tiny files.

## References

- [ffmpeg — security](https://ffmpeg.org/security.html)
- [0xdf — Player](https://0xdf.gitlab.io/2020/01/18/htb-player.html)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)

# MTE Capstone Development Log

A static website for our capstone dev logs, meeting minutes and project
documents. There is no database and no login — every entry is a Markdown file
in this repository, and the site rebuilds itself whenever someone pushes.

**Live site:** `https://<username>.github.io/<repo>/`

---

## Adding an entry (no git required)

You can do all of this from github.com in a browser.

1. Open the **`logs/`** folder (or **`minutes/`** for meeting minutes).
2. Click **Add file → Create new file**.
3. Name it `YYYY-MM-DD-short-title.md` — for example
   `2026-10-03-encoder-mount-redesign.md`. The date in the filename is what
   orders the site, so keep the format.
4. Paste the template below and write your entry.
5. Scroll down, click **Commit changes**.

The site updates itself about 30 seconds later. You do not need to touch
`index.html` or `content/index.json` — those are handled for you.

### Dev log template

```markdown
---
title: Encoder mount redesign
date: 2026-10-03
author: [Your Name]
tags: [mechanical, testing]
attachments:
  - docs/encoder-bracket-rev-B.pdf
---

# Encoder mount redesign

What you did, what you found, and what it means for the project.
```

Copies of both templates live at [`logs/_TEMPLATE.md`](logs/_TEMPLATE.md) and
[`minutes/_TEMPLATE.md`](minutes/_TEMPLATE.md). Files starting with `_` are
ignored by the site, so the templates never show up as entries.

## Attaching a PDF or image

1. Open the **`docs/`** folder.
2. Click **Add file → Upload files** and drag your PDF in.
3. Commit.
4. Reference it from an entry in the `attachments:` list:

```yaml
attachments:
  - docs/your-file.pdf
```

Attached files appear as download links at the bottom of the entry, and every
file in `docs/` is also listed under the **Documents** tab — with a note saying
which entries cite it. Linking to a file inline with normal Markdown
(`[the drawing](docs/your-file.pdf)`) also registers it as an attachment.

## Editing an existing entry

Open the `.md` file on github.com, click the **pencil icon**, edit, commit. The
site picks up the change on its own and labels the entry "updated" with the new
date. The old version is still in the commit history, which is worth knowing —
nothing you write here is ever really lost.

## Front matter reference

Everything between the `---` lines at the top of a file.

| Field | Applies to | Notes |
| --- | --- | --- |
| `title` | both | Falls back to the first `#` heading, then the filename. |
| `date` | both | `YYYY-MM-DD`. Falls back to the date in the filename. |
| `author` | dev logs | One name or a list: `[Ann, Ben]`. |
| `attendees` | minutes | Who was at the meeting. |
| `tags` | both | Becomes the filter buttons on the site. |
| `attachments` | both | Paths relative to the repo root. |
| `summary` | both | One-line blurb for the list view. Auto-generated if omitted. |
| `type` | both | Only needed to override the folder (`log` or `minutes`). |
| `updated` | both | Only needed to override the git history date. |

Every field is optional. A file with no front matter at all still works.

---

## Site setup (once)

1. Create a GitHub repo and push this folder to the `main` branch.
2. **Settings → Pages → Build and deployment → Deploy from a branch**, then
   pick `main` and `/ (root)`. Save.
3. **Settings → Actions → General → Workflow permissions**, select
   **Read and write permissions**. This lets the index rebuild itself; without
   it, new entries will not appear.
4. Edit the `site-config` block near the top of
   [`index.html`](index.html) — project name, course code, term, team names.

## How it works

- [`scripts/build_index.py`](scripts/build_index.py) scans `logs/`, `minutes/`
  and `docs/`, reads the front matter, and writes `content/index.json`.
- [`.github/workflows/build-index.yml`](.github/workflows/build-index.yml) runs
  that script on every push and commits the result back.
- `index.html` is a single page that fetches `content/index.json` and renders
  it. No framework, no build step, no dependencies to install.

### Previewing locally

Only needed if you want to see changes before pushing:

```bash
python3 scripts/build_index.py   # rebuild the index
python3 -m http.server 8000      # then open http://localhost:8000
```

Opening `index.html` directly as a `file://` URL will not work — browsers block
the index fetch. Use the local server.

### Printing an entry

Open any entry and print it (⌘P / Ctrl+P). The page layout drops away and you
get a clean, letterheaded document with the Waterloo mark at the top — useful
for handing minutes to an advisor or attaching a log to a report.

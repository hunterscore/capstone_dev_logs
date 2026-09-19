# MTE Capstone Development Log

A static website for our capstone meeting minutes, project ideas, dev logs
and project documents. There is no database and no login — every entry is a Markdown file
in this repository, and the site rebuilds itself whenever someone pushes.

**Live site:** `https://<username>.github.io/<repo>/`

---

## Adding an entry (no git required)

You can do all of this from github.com in a browser.

1. Open the folder for the kind of entry:
   - **`minutes/`** — meeting minutes
   - **`ideas/`** — candidate project ideas, while the project is being chosen
   - **`logs/`** — development logs, once work is underway
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

Templates for each kind live at [`minutes/_TEMPLATE.md`](minutes/_TEMPLATE.md),
[`ideas/_TEMPLATE.md`](ideas/_TEMPLATE.md) and [`logs/_TEMPLATE.md`](logs/_TEMPLATE.md). Files starting with `_` are
ignored by the site, so the templates never show up as entries.

## Project ideas

Each idea gets its own file in `ideas/`. Set `status:` to one of:

| Status | Meaning |
| --- | --- |
| `considering` | On the table (the default) |
| `shortlisted` | Still in the running after a first cut |
| `selected` | The project we are doing |
| `rejected` | Dropped. Keep the file and note why under *Decision notes* — the record of what was ruled out, and why, is useful when writing the proposal. |

The **Project Ideas** tab groups ideas by status. Once a project is chosen, update
`project` and `status` in the `site-config` block of `index.html`.

## Drafts

Add `draft: true` to an entry's front matter to keep it off the site while it is
being written. Delete that line when it's ready. [`minutes/group-formation.md`](minutes/group-formation.md)
starts out as a draft.

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
| `title` | all | Falls back to the first `#` heading, then the filename. |
| `date` | all | `YYYY-MM-DD`. Falls back to the date in the filename. |
| `author` | logs, ideas | One name or a list: `[Ann, Ben]`. Shown as "Proposed by" on ideas. |
| `attendees` | minutes | Who was at the meeting. |
| `status` | ideas | `considering`, `shortlisted`, `selected` or `rejected`. |
| `draft` | all | `true` keeps the entry off the site. |
| `tags` | all | Becomes the filter buttons on the site. |
| `attachments` | all | Paths relative to the repo root. |
| `summary` | all | One-line blurb for the list view. Auto-generated if omitted. |
| `type` | all | Only needed to override the folder (`log`, `minutes` or `idea`). |
| `updated` | all | Only needed to override the git history date. |

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

- [`scripts/build_index.py`](scripts/build_index.py) scans `minutes/`, `ideas/`,
  `logs/` and `docs/`, reads the front matter, and writes `content/index.json`.
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

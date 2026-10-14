---
name: add-visit
description: Add a visit to the Weird 300 blog from Tim's photos and notes. Imports and cleans the photos, writes the page and its write-up, validates it, previews it with Tim, and publishes. Use when Tim shares photos or notes about a place he visited, or says he went somewhere from the book.
---

# Add a visit

Read `CLAUDE.md` first; its writing rules apply to everything below.

## 1. Gather

You need: the place name, photos (3 to 5 is typical), and Tim's notes.
Useful extras: a Google Maps link, who came along, the book's entry or page
number. Ask once for anything missing that the page requires (the category
is required; pick the obvious one from `_data/categories.yml` and confirm).

Photos must be inside the repo, because macOS blocks this terminal from
reading `~/Desktop` and `~/Downloads`. Ask for the originals off the camera or
phone rather than exports, since step 2 archives them for print. Ask Tim to
run:

```sh
mkdir -p ~/Code/Weird300/inbox && open ~/Code/Weird300/inbox
```

That opens the inbox in Finder; Tim drags the folder in. Do not hand him a
`mv` with the folder name typed out: Finder names often differ from what he
says (the Fingal's Cave folder was really `Fingals Cave`).

A Google Maps short link resolves with
`curl -sIL <link> | /usr/bin/grep -i ^location`; the `!3d<lat>!4d<lng>`
pair in the result is the pin. (Plain `grep` is shimmed on this machine;
use `/usr/bin/grep`.)

## 2. Archive the originals

Before the import shrinks anything. The site's copies are 1600px with the
metadata stripped, and a photo book needs what came off the camera.

```sh
uv run scripts/archive_originals.py "<Name>" inbox/<folder>     # --dry-run to see the plan first
```

It uploads to Google Drive through the `weird300` rclone remote as
`YYYY-MM-DD - Name - NN.jpg`, verifies every file by checksum, and writes
`originals/<slug>.yml`. Commit that manifest with the visit.

If it reports that the remote is not set up, stop and tell Tim: the one-time
`rclone config` needs a browser, so only he can do it. Do not carry on and
delete his only copies.

## 3. Import

```sh
uv run scripts/new_visit.py "<Name>" inbox/<folder> --category "<Category>" \
  --region "<Place, Area>" --with "<companions>" [--lat .. --lng ..]
```

Pass `--lat/--lng` from the Maps pin when you have it; photo GPS is where
Tim stood, not where the place is. If the page already exists (drafted
before photos arrived), the same command appends the photos. Read the JSON
summary: if `visited` was still TODO and the photos carry a date, set it.

## 4. Look at the photos

Read each imported file in `assets/photos/<slug>/` so you actually see it.
Then:

- Reorder the `photos:` list so the strongest shot is first. It is the hero
  and the card image. A `landscape` cover becomes a full-width banner; a
  `portrait` one is shown whole beside the title. The hero is cropped to a wide banner, so for a
  tall photo add `focus: "50% 25%"` (or whatever keeps the subject in frame).
- Write a short caption for each, describing what is in frame. Never guess
  at things you cannot see.

## 5. Write

Front matter: fill `summary` (one sentence, used for link previews) and any
remaining TODO. Body: three or four short paragraphs from Tim's notes, in his
voice. One or two well-established facts about the place are fine. Nothing
about the visit itself that he did not tell you.

## 6. Check and preview

```sh
uv run scripts/check.py
```

It must print `ok` for every page. Then show Tim the write-up and captions
in the chat and ask for changes. Do not push until he approves.

## 7. Publish

```sh
git add _places/<slug>.md assets/photos/<slug> && git commit -m "Add <Name>"
git push
```

Wait about a minute, confirm with
`gh api repos/tchingos/weird300/pages/builds/latest --jq '.status, .error.message'`,
then give Tim the page URL:
`https://tchingos.github.io/weird300/places/<slug>/`.

Only now, after the page is live AND `originals/<slug>.yml` exists, delete the
raw photos from `inbox/`. No manifest means the originals are not safe
anywhere, so leave them where they are and say so.

## 8. Draft the "new post" email

Tim emails close friends and family about each new post himself. Your job is
only the draft; never send anything.

Do not use the Gmail connector for this. It rewrites every link into a
google.com redirect, and readers then hit a "Redirect Notice" page.

1. Write `emails/<slug>.txt` (git-ignored): the subject on the first line,
   a blank line, then a short plain-text note in Tim's voice (two or three
   sentences, same writing rules, no em dashes), the post's full `https://`
   link on its own line, and "Tim" at the end. Plain text only; no images.
   Subject: `New on Weird 300: <Title>`.
2. Run `python3 scripts/compose_email.py emails/<slug>.txt`. It opens a
   Gmail compose window addressed to Tim with everyone in
   `~/.config/weird300/subscribers.txt` in BCC.
3. Tell Tim the compose window is open for him to proofread and send. If he
   closes it by accident, run the same command again.

If the list is empty, skip the draft and tell Tim.

For a journal post (anything that is not one of the 300) the steps are the
same, using `uv run scripts/new_post.py "<Title>" inbox --date YYYY-MM-DD`.

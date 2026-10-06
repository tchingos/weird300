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
reading `~/Desktop` and `~/Downloads`. Ask Tim to run:

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

## 2. Import

```sh
uv run scripts/new_visit.py "<Name>" inbox/<folder> --category "<Category>" \
  --region "<Place, Area>" --with "<companions>" [--lat .. --lng ..]
```

Pass `--lat/--lng` from the Maps pin when you have it; photo GPS is where
Tim stood, not where the place is. If the page already exists (drafted
before photos arrived), the same command appends the photos. Read the JSON
summary: if `visited` was still TODO and the photos carry a date, set it.

## 3. Look at the photos

Read each imported file in `assets/photos/<slug>/` so you actually see it.
Then:

- Reorder the `photos:` list so the strongest wide shot is first. It is the
  hero and the card image. The hero is cropped to a wide banner, so for a
  tall photo add `focus: "50% 25%"` (or whatever keeps the subject in frame).
- Write a short caption for each, describing what is in frame. Never guess
  at things you cannot see.

## 4. Write

Front matter: fill `summary` (one sentence, used for link previews) and any
remaining TODO. Body: three or four short paragraphs from Tim's notes, in his
voice. One or two well-established facts about the place are fine. Nothing
about the visit itself that he did not tell you.

## 5. Check and preview

```sh
uv run scripts/check.py
```

It must print `ok` for every page. Then show Tim the write-up and captions
in the chat and ask for changes. Do not push until he approves.

## 6. Publish

```sh
git add _places/<slug>.md assets/photos/<slug> && git commit -m "Add <Name>"
git push
```

Wait about a minute, confirm with
`gh api repos/tchingos/weird300/pages/builds/latest --jq '.status, .error.message'`,
then give Tim the page URL:
`https://tchingos.github.io/weird300/places/<slug>/`.
Finally, delete the raw folder from `inbox/`.

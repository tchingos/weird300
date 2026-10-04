# Weird 300

Our progress through the 300 places in *Weird Guide Britain* by Dave
Hamilton. Live at https://tchingos.github.io/weird300/.

Each visit is a Markdown page in `_places/` with its photos in
`assets/photos/<slug>/`. Add one with:

```sh
uv run scripts/new_visit.py "Place Name" inbox/<photo-folder> --category "Follies" --region "Town, County"
uv run scripts/check.py
```

See `CLAUDE.md` for the layout and writing rules.

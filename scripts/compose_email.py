"""Open a pre-filled Gmail compose window for a "new post" email.

    python3 scripts/compose_email.py emails/<name>.txt

The file's first line is the subject; everything after the first blank line
is the plain-text body. Recipients are Tim (To) and everyone in
~/.config/weird300/subscribers.txt (BCC). Nothing is sent: Tim proofreads and
clicks Send in Gmail.

Why not the Gmail connector: it rewrites every link into a google.com
redirect that shows readers a "Redirect Notice" page. Text typed into
Gmail's own compose window keeps its links direct.
"""

import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ME = "timothy.a.chingos@gmail.com"
SUBSCRIBERS = Path.home() / ".config" / "weird300" / "subscribers.txt"


def subscribers() -> list[str]:
    lines = (re.sub(r"#.*", "", line).strip() for line in SUBSCRIBERS.read_text().splitlines())
    return [line for line in lines if line]


def main() -> None:
    subject, _, body = Path(sys.argv[1]).read_text().strip().partition("\n\n")
    bcc = subscribers()
    if not bcc:
        sys.exit(f"No subscribers in {SUBSCRIBERS}")
    params = {"view": "cm", "fs": "1", "authuser": ME, "to": ME, "bcc": ",".join(bcc), "su": subject.strip(), "body": body.strip()}
    subprocess.run(["open", "https://mail.google.com/mail/?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)], check=True)
    print(f"Opened Gmail compose: {subject.strip()!r} to {ME}, BCC {len(bcc)}")


if __name__ == "__main__":
    main()

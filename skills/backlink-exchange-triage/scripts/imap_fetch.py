#!/usr/bin/env python3
"""Read-only IMAP fetcher for the backlink-exchange-triage skill.

Opens folders read-only and fetches with BODY.PEEK, so nothing is marked as read,
moved or changed. Python standard library only.

Credentials come from a .env file (--env) or the environment:
    IMAP_HOST, IMAP_USER, IMAP_PASSWORD, optional IMAP_PORT (default 993)
They are never printed.

Examples:
    python -I imap_fetch.py --env .env --list-folders
    python -I imap_fetch.py --env .env --folder INBOX --since 2026-01-01 --out inbox.json
    python -I imap_fetch.py --env .env --folder INBOX --since 2026-01-01 \
        --subject-has "link" --subject-has "guest post" --out inbox.json
"""
import argparse, datetime, email, html, imaplib, json, os, re, sys
from email import policy
from email.utils import parsedate_to_datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_env(path):
    env = dict(os.environ)
    if path:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD"):
        if not env.get(k):
            sys.exit(f"missing {k} (set it in the .env file or the environment)")
    return env


def quote_folder(name):
    return '"' + name.replace("\\", "\\\\").replace('"', '\\"') + '"'


def html_to_text(raw):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", t, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return t


def body_text(msg):
    plain, htm = None, None
    for part in msg.walk():
        if part.get_content_maintype() == "multipart" or part.get_filename():
            continue
        ctype = part.get_content_type()
        try:
            content = part.get_content()
        except Exception:
            payload = part.get_payload(decode=True) or b""
            content = payload.decode(part.get_content_charset() or "utf-8", "replace")
        if ctype == "text/plain" and plain is None:
            plain = content
        elif ctype == "text/html" and htm is None:
            htm = content
    text = plain if plain else html_to_text(htm or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text


def strip_quoted(text):
    # Cut the quoted history so each message holds only what that sender wrote.
    cut = re.split(r"\n\s*On .{5,160}wrote:|\n-{2,} ?Original Message|\nFrom: .{3,120}\n(Sent|Date): ", text)
    text = cut[0]
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">")).strip()


def subject_query(words):
    if not words:
        return []
    q = ["SUBJECT", quote_folder(words[-1])]
    for w in reversed(words[:-1]):
        q = ["OR", "SUBJECT", quote_folder(w)] + q
    return q


def main():
    ap = argparse.ArgumentParser(description="Read-only IMAP fetch to JSON")
    ap.add_argument("--env", help="path to a .env file with IMAP_HOST, IMAP_USER, IMAP_PASSWORD")
    ap.add_argument("--list-folders", action="store_true", help="list folders and exit")
    ap.add_argument("--folder", default="INBOX")
    ap.add_argument("--since", help="YYYY-MM-DD (default: 90 days ago)")
    ap.add_argument("--subject-has", action="append", default=[], help="subject contains (repeatable, OR-ed)")
    ap.add_argument("--max", type=int, default=1000, help="newest N messages at most")
    ap.add_argument("--body-chars", type=int, default=4000)
    ap.add_argument("--keep-quoted", action="store_true", help="keep quoted reply history in bodies")
    ap.add_argument("--headers-only", action="store_true", help="sender, subject, date and ids only (cheap first pass)")
    ap.add_argument("--out", help="JSON output path (required unless --list-folders)")
    a = ap.parse_args()

    env = load_env(a.env)
    conn = imaplib.IMAP4_SSL(env["IMAP_HOST"], int(env.get("IMAP_PORT", 993)))
    try:
        conn.login(env["IMAP_USER"], env["IMAP_PASSWORD"])
    except imaplib.IMAP4.error as e:
        sys.exit(f"login failed: {e}. Check the host, the user name and that the password is an app password.")

    if a.list_folders:
        typ, data = conn.list()
        for line in data or []:
            s = line.decode("utf-8", "replace")
            m = re.search(r'"([^"]*)"$|(\S+)$', s)
            name = m.group(1) if m and m.group(1) is not None else (m.group(2) if m else s)
            typ2, cnt = conn.select(quote_folder(name), readonly=True)
            n = cnt[0].decode() if typ2 == "OK" else "?"
            print(f"{name}: {n} messages")
        conn.logout()
        return

    if not a.out:
        sys.exit("--out is required")
    since = a.since or (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    since_imap = datetime.date.fromisoformat(since).strftime("%d-%b-%Y")

    typ, _ = conn.select(quote_folder(a.folder), readonly=True)
    if typ != "OK":
        sys.exit(f"cannot open folder {a.folder!r}; run --list-folders to see the names")
    criteria = ["SINCE", since_imap] + subject_query(a.subject_has)
    typ, data = conn.search(None, *criteria)
    ids = data[0].split()[-a.max:] if data and data[0] else []

    out = []
    for i in ids:
        part = "(BODY.PEEK[HEADER])" if a.headers_only else "(BODY.PEEK[])"
        typ, msg_data = conn.fetch(i, part)
        raw = next((p[1] for p in msg_data if isinstance(p, tuple)), None)
        if not raw:
            continue
        msg = email.message_from_bytes(raw, policy=policy.default)
        try:
            dt = parsedate_to_datetime(msg["Date"]).astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
        except Exception:
            dt = ""
        text = "" if a.headers_only else body_text(msg)
        if text and not a.keep_quoted:
            text = strip_quoted(text)
        out.append({
            "folder": a.folder,
            "date_utc": dt,
            "from": str(msg.get("From", "")),
            "to": str(msg.get("To", "")),
            "cc": str(msg.get("Cc", "")),
            "subject": str(msg.get("Subject", "")),
            "message_id": str(msg.get("Message-ID", "")),
            "in_reply_to": str(msg.get("In-Reply-To", "")),
            "references": str(msg.get("References", "")),
            "body": text[: a.body_chars],
        })
    conn.logout()
    out.sort(key=lambda r: r["date_utc"])
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"saved {len(out)} messages from {a.folder} since {since} to {a.out}")


if __name__ == "__main__":
    main()

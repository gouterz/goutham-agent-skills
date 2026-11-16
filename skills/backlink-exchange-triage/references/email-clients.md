# Connecting the email client

Providers change their settings, scopes and screens, so **look up the current official steps for the user's client** with a web search, and prefer the provider's own help pages over blog posts. Good searches: "<client> IMAP app password", "<client> API OAuth read only scope", "<client> send email API scope", "<client> export mailbox". This file says what to look for and how to stay safe. It isn't a recipe for any one provider.

## Contents
1. Rules for every connection
2. Permission by sending level
3. Option 1: the agent already has an email tool
4. Option 2: IMAP, with `scripts/imap_fetch.py`
5. Option 3: the provider's API (OAuth)
6. Option 4: an export file (no live access)
7. Replying in the right thread (drafts and sending only)
8. Common snags

## 1. Rules for every connection

- **The narrowest permission that does the job** (section 2). Never full mailbox access, delete, settings or admin scopes.
- **The user creates the credential** (app password, OAuth client, API token) and puts it in a `.env` file or the shell environment, not in git. The agent loads it by variable name and never prints it, echoes it or writes it to another file. If the user pastes a secret into the chat, tell them to revoke it and make a new one.
- **Test before triaging:** list folder names, message counts and the newest date. No subjects or bodies in the test output.
- **Save what you learned** (server, port, region or data center, folder names) in the config, without secrets.
- **Tell the user how to revoke access** when they're done: delete the app password, OAuth client or token in the provider's security settings.

## 2. Permission by sending level

The level comes from setup question 8. Look up the exact scope names in the provider's docs; these are examples.

| Level | Ask for | Examples |
|---|---|---|
| a. Replies in chat (default) | Read only | Gmail `gmail.readonly`; Microsoft Graph `Mail.Read`; a provider's "messages read" scope; IMAP |
| b. Save drafts | Read + create drafts | Gmail `gmail.readonly` + `gmail.compose`; Graph `Mail.Read` + `Mail.ReadWrite` (Graph needs ReadWrite for drafts) |
| c. Send after approval | Read + send | Gmail `gmail.readonly` + `gmail.send`; Graph `Mail.Read` + `Mail.Send`; IMAP + SMTP |

- If the provider has no send-only or draft-only scope, say so, choose the smallest one it does have, and explain what else it allows.
- An app password usually covers both IMAP (read) and SMTP (send) and can't be narrowed. That's fine for level c, but for level a the agent must still never use SMTP. Suggest revoking the app password after the run.
- For levels b and c, the user approves each email in chat first (SKILL.md, Step 6).

## 3. Option 1: the agent already has an email tool

If the agent already has a mail connector or MCP server for the user's client, use it, and check what it can do:
- Use only the actions the user's sending level allows. For level a, ignore its send, draft, label, move and delete actions.
- Learn its search syntax from its own description. For example, Gmail uses `newer_than:30d ("link exchange" OR "guest post")`, and Outlook uses KQL such as `"link exchange" received>=2026-01-01`.
- List headers first and read bodies only for the threads you keep (the reading budget).

## 4. Option 2: IMAP, with `scripts/imap_fetch.py`

Most providers offer IMAP: webmail services, most hosting providers (cPanel, Plesk), and some privacy services through a local bridge app. Look up the provider's IMAP host and whether it needs an app password.

1. The user turns IMAP on in the mail settings if it's off, and creates an **app password** (most providers need 2-step verification first).
2. In `.env`:
   ```
   IMAP_HOST=imap.example.com
   IMAP_USER=you@example.com
   IMAP_PASSWORD=the-app-password
   ```
   Add `IMAP_PORT` if it isn't 993.
3. Test, folder names and counts only:
   ```
   python -I scripts/imap_fetch.py --env .env --list-folders
   ```
4. List the window cheaply (senders, subjects, dates; no bodies):
   ```
   python -I scripts/imap_fetch.py --env .env --folder INBOX --since 2026-01-01 --headers-only --max 300 --out scratch/inbox-headers.json
   ```
5. Read bodies only for what you keep, narrowing on the server with subject words:
   ```
   python -I scripts/imap_fetch.py --env .env --folder INBOX --since 2026-01-01 --subject-has "link" --subject-has "guest post" --max 40 --out scratch/inbox.json
   ```
   Do the same for the Sent folder (its name varies by provider, so check `--list-folders`).

The script opens folders read-only and fetches with `BODY.PEEK`, so nothing is marked as read. It can't send. For level c over SMTP, write a small separate sender that uses the same `.env`, sends only the approved emails, and threads them (section 7).

## 5. Option 3: the provider's API (OAuth)

Use this when IMAP is off, blocked or harder to set up. Look up the provider's API docs for:
- **Where to create the client:** a developer or API console (an OAuth client, an app registration or a "self client"), and whether the account's **region or data center** changes the URLs.
- **The scopes** for the sending level (section 2).
- **How to get a refresh token once** (an authorization-code or device-code flow) and an access token each run.
- **The calls for:** listing folders, listing messages in a folder (newest first, paged), searching, reading one message's body, and the Sent folder. Plus, for levels b and c, creating a draft and sending a reply.

Then keep `CLIENT_ID`, `CLIENT_SECRET` and `REFRESH_TOKEN` (and the region, if any) in `.env`, write a small script that gets an access token and makes only those calls, and test with folder names and counts.

## 6. Option 4: an export file (no live access)

If the user doesn't want to connect anything, they export the relevant folders, the Sent folder included, and the agent reads the file. Look up the client's export steps. Most can export `.mbox`, or save messages as `.eml` files.

Read `.mbox` with Python's `mailbox.mbox(path)` and `.eml` files with `email.message_from_binary_file`. Replies can only be shown in chat in this mode.

## 7. Replying in the right thread (drafts and sending only)

- Reply to the thread's last message from the partner: same subject with "Re:", the partner's address as recipient, and any cc the user approved.
- Set `In-Reply-To` to that message's `Message-ID`, and `References` to its `References` plus its `Message-ID`. APIs usually also take a thread or conversation id; use it.
- Over SMTP, save a copy to the Sent folder if the provider doesn't do it.
- After sending, read the Sent folder back to confirm.

## 8. Common snags

- **Password rejected over IMAP:** the provider may need an app password, or may have turned off passwords for IMAP altogether (some large providers now require OAuth). Look it up, then switch to Option 3 or a connector.
- **`invalid_client` or unknown-user errors from an OAuth token URL:** often the wrong region or data center. Look up the provider's regional URLs, try the user's region first, and save the one that works in the config.
- **403 from an API with correct credentials:** some APIs block default script user agents. Send a normal browser-like `User-Agent` header.
- **Search returns too much:** many search APIs match each word separately and search every folder. Put phrases in quotes, limit by folder and date, and list headers before reading bodies.
- **Slow body fetching:** many APIs return 1 body per call. Fetch bodies only for the threads you keep, and tell the user how many that is before a big fetch.
- **Warmup emails:** if the mailbox is also used by a cold-email sending tool, it carries that tool's warmup emails. Filter them out before counting anything.

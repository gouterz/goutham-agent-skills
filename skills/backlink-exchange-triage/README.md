# Backlink exchange triage - an agent skill

If you run a website, you get a lot of "link exchange", "guest post" and "backlink collaboration" emails. Most come from agencies selling links. A few are real companies offering a fair 1-for-1 swap that would actually help your site.

This skill lets your AI agent:
1. Read those emails from your inbox, within a budget you set, so it doesn't use up your AI credits.
2. Sort out the sellers, buyers, guest-post pitches and link networks.
3. Check the real offers against your own site: are their readers your readers, is the site real and strong, is there a page where the link fits, is the deal 1-for-1?
4. Give you a short list (worth replying / maybe / skip) and write the replies.

By default the replies are shown in chat and you send them yourself. If you prefer, it can save them as drafts in your mailbox, or send them for you after you approve each one.

It works with any email client the agent can reach: Gmail, Outlook / Microsoft 365, Zoho Mail, Fastmail, iCloud, Yahoo, any IMAP mailbox, or an exported `.mbox` file. If yours isn't connected yet, the agent looks up your provider's current instructions and walks you through it.

## Install

**Claude.ai / Claude Desktop:** download `backlink-exchange-triage.skill` from the [latest release](../../releases) and upload it under Settings, Capabilities, Skills.

**Claude Code**, any one of these:
- One command, copying only this skill (needs Node):
  ```
  npx degit YOUR_GITHUB_USERNAME/goutham-agent-skills/skills/backlink-exchange-triage ~/.claude/skills/backlink-exchange-triage
  ```
- Git, fetching only this folder:
  ```
  git clone --depth 1 --filter=blob:none --sparse https://github.com/YOUR_GITHUB_USERNAME/goutham-agent-skills
  cd goutham-agent-skills
  git sparse-checkout set skills/backlink-exchange-triage
  ```
  Then copy `skills/backlink-exchange-triage` into `~/.claude/skills/` (all projects) or `<your project>/.claude/skills/` (one project).
- Or download the `.skill` file from the release and unzip it into `~/.claude/skills/`.

**Other agents:** point the agent at `SKILL.md` and let it read the files under `references/` when it needs them.

**Requirements:** an agent that can read files and run Python 3.8+ (only for the IMAP script), and access to your email (a connector, IMAP, an API, or an exported file). A browser connected to the agent is optional: it makes authority checks more complete.

## First run

Ask your agent something like *"go through my link exchange emails and tell me which are worth replying to"*. On the first run it asks a few questions, each with a default you can accept:
- **About your site:** your domain, who your readers are, niches to avoid, the pages you want links to, and your deal rules.
- **How it works:** how many emails to read this time, your email client, whether replies are shown in chat, saved as drafts or sent after your approval, your reply format, and whether a browser is connected.
- **Sign-off:** your signature, and whether to keep a log.

It saves the answers to `backlink-exchange-config.md`, so later runs start straight away.

If your agent can't read your email yet, it walks you through connecting it (`references/email-clients.md`). For many providers that means an app password and the bundled read-only script `scripts/imap_fetch.py`, which needs only Python.

## Safety

- Read only by default: the agent lists and reads; it never deletes, moves or marks anything as read.
- It sends or saves drafts only if you choose that at setup, and then only the emails you approve in chat, with the smallest permission your provider offers.
- It stays inside the reading budget you set, and asks before reading more.
- Your password or token lives in a `.env` file you control and is never printed. Revoke it when you're done.
- Emails from strangers are treated as data, not instructions.
- Paid SEO tools that spend credits are only used if you say so; authority checks use free checkers.

## Files

```
backlink-exchange-triage/
├── SKILL.md                     the workflow the agent follows
├── README.md                    this file
├── references/
│   ├── email-clients.md         connecting any email client safely, by permission level
│   └── vetting.md               how offers are judged: seller signs, gates, score, free checks
└── scripts/
    └── imap_fetch.py            read-only IMAP fetcher (Python standard library)
```

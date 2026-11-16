# Goutham's agent skills

Practical skills for AI agents, written for founders and site owners who'd rather not spend the day in their inbox. Each skill is a folder of plain Markdown instructions (plus small scripts where needed) that teaches an agent such as Claude to do one job well and safely.

## Featured: Backlink exchange triage

**"Quick link exchange idea for your site 🤝" usually means "what are your rates?"**

This skill reads the link-exchange, guest-post and "backlink collaboration" emails in your inbox, sorts out the link sellers, link buyers, guest-post pitches and "ABC swap" networks, and checks the few real offers against your own site:
- Do their readers match yours?
- Is the site real, with real authority?
- Is there a page where the link actually fits?
- Is it a fair 1-for-1 deal?

Then it writes the replies, each with the exact edit for the publisher to make:

```
Target link: <their article>
Destination page: <your page>
Anchor text: <the linked words>
After (in "<section>"): <the existing sentence>
Add: <the new sentence>
```

It works with any email client, stays inside a reading budget you set so it doesn't burn your AI credits, and is read only by default: replies are shown to you to send, unless you choose drafts or sending after approving each email.

**[Open the skill →](skills/backlink-exchange-triage/)**

## Skills

| Skill | What it does | Works with |
|---|---|---|
| [backlink-exchange-triage](skills/backlink-exchange-triage/) | Finds the link-exchange emails worth answering and writes the replies | Claude Code, Claude.ai, other agents that read Markdown skills; any email client |

More skills are on the way.

## Installing a skill

Each skill's own README has the full steps. In short:

- **Claude.ai / Claude Desktop:** download the skill's `.skill` file from [Releases](../../releases) and upload it under Settings, Capabilities, Skills.
- **Claude Code:** copy the skill's folder into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/` (one project). To copy a single skill without cloning the whole repo:
  ```
  npx degit YOUR_GITHUB_USERNAME/goutham-agent-skills/skills/<skill-name> ~/.claude/skills/<skill-name>
  ```
- **Other agents:** point the agent at the skill's `SKILL.md`; it reads the files under `references/` when it needs them.

## Principles every skill here follows

- **Safe by default:** read-only access unless you opt in, the smallest permission that does the job, and nothing sent or changed without your approval.
- **Your secrets stay yours:** credentials live in your own `.env` file and are never printed or stored by the skill.
- **Cheap to run:** skills set a budget up front and ask before reading or doing more.
- **No lock-in:** plain Markdown and standard-library scripts; no accounts, servers or paid tools required.

## License

[MIT](LICENSE). Use them, change them, share them.

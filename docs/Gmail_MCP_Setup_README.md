# Gmail MCP Server Setup

This guide covers end-to-end setup of the Gmail MCP server (`@gongrzhe/server-gmail-autoauth-mcp`) so the agent can send, read, and search emails.

---

## 1. Google Cloud Console Setup

### 1.1 Create a Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown (top bar) → **New Project**
3. Name it (e.g. `my-claude-agent`) and click **Create**

### 1.2 Enable the Gmail API
1. Go to **APIs & Services → Enable APIs & Services**
2. Search for **Gmail API** and click it
3. Click **Enable**

### 1.3 Configure the OAuth Consent Screen
1. Go to **APIs & Services → OAuth consent screen**
2. Choose **External** (works for personal Gmail accounts) → **Create**
3. Fill in:
   - **App name**: anything (e.g. `My Claude`)
   - **User support email**: your Gmail address
   - **Developer contact email**: your Gmail address
4. Click **Save and Continue** through Scopes and Summary
5. On the **Test users** page, click **Add users** and add your Gmail address
6. Click **Save and Continue**

> **Why test users?** While the app is in "Testing" mode, only listed emails can authorize it. Without adding yourself here, the OAuth consent screen will be blocked.

### 1.4 Create OAuth Credentials
1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Choose **Desktop app** as the application type
4. Give it a name and click **Create**
5. Click **Download JSON** — this is your `credentials.json`

---

## 2. Local Setup

### 2.1 Place the credentials file
The server looks for credentials in `~/.gmail-mcp/gcp-oauth.keys.json`:

```bash
mkdir -p ~/.gmail-mcp
cp capstone_project/my_claude/credentials.json ~/.gmail-mcp/gcp-oauth.keys.json
```

### 2.2 Run the one-time OAuth flow

> Make sure port 3000 is free before running this. If something is already using it:
> ```bash
> lsof -i :3000 | grep LISTEN   # find the PID
> kill <PID>
> ```

Then run:

```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

This will:
- Start a local server on port 3000 to receive the OAuth callback
- Open your browser at Google's consent screen
- Ask you to sign in and grant Gmail access
- Save the access + refresh token to `~/.gmail-mcp/credentials.json`

After this, tokens are **auto-refreshed** — you never need to repeat this step.

---

## 3. Project Configuration

### mcp_servers.json
```json
"gmailserver": {
    "command": "npx",
    "transport": "stdio",
    "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"]
}
```

No env vars needed — the server reads credentials from `~/.gmail-mcp/` automatically.

### config.yaml
```yaml
mcp:
  gmailserver:
    selected_tools:
      [
        "send_email",
        "read_email",
        "search_emails",
        "list_emails"
      ]
```

---

## 4. Available Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email with subject, body (plain/HTML), cc, bcc, attachments |
| `read_email` | Read a specific email by ID |
| `search_emails` | Search emails by subject, sender, date range, labels |
| `list_emails` | List emails in inbox, sent, or any label |
| `modify_email` | Mark as read/unread, move to label |
| `delete_email` | Delete an email |

---

## 5. Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `EADDRINUSE port 3000` | Another process is using port 3000 | `kill $(lsof -t -i:3000)` then retry |
| `No access, refresh token` | OAuth flow not completed | Run `npx @gongrzhe/server-gmail-autoauth-mcp auth` |
| `Access blocked` on consent screen | Your email not added as test user | Add it in Cloud Console → OAuth consent screen → Test users |
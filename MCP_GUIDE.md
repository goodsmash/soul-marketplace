# MCP Integration Guide

## Model Context Protocol (MCP)

Soul Marketplace implements MCP for compatibility with Claude Desktop, Cursor, Claude Code, and any MCP-compatible client.

## Installation

### For Claude Desktop

1. **Open Claude Desktop Settings**
   - macOS: `Cmd + ,`
   - Windows/Linux: `Ctrl + ,`

2. **Edit MCP Settings**
   Click "Edit Config" to open `claude_desktop_config.json`

3. **Add Soul Marketplace Server**
   ```json
   {
     "mcpServers": {
       "soul-marketplace": {
         "command": "node",
         "args": [
           "/home/goodsmash/.openclaw/skills/soul-marketplace/mcp-server.js"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Verify**
   Look for the 🔨 tools icon in the chat interface. You should see:
   - `check_survival_status`
   - `record_work`
   - `heartbeat`
   - `list_soul`
   - `calculate_soul_value`

### For Cursor

1. **Open Cursor Settings**
   - `Cmd/Ctrl + Shift + P` → "Cursor Settings"

2. **Go to MCP Section**

3. **Add Server**
   ```json
   {
     "mcpServers": {
       "soul-marketplace": {
         "command": "node",
         "args": [
           "/home/goodsmash/.openclaw/skills/soul-marketplace/mcp-server.js"
         ]
       }
     }
   }
   ```

### For Claude Code

Add to your Claude Code configuration:

```bash
claude config set mcpServers '{"soul-marketplace":{"command":"node","args":["/home/goodsmash/.openclaw/skills/soul-marketplace/mcp-server.js"]}}'
```

## Available Tools

### check_survival_status
Check current survival tier, balance, and overall agent status.

**Usage:**
```
Claude: "Check my survival status"
```

### record_work
Record completed work to earn survival credits.

**Parameters:**
- `work_type`: Type of work (code_generate, file_edit, web_search, etc.)
- `description`: Description of what was done

**Usage:**
```
Claude: "I just built a new feature"
Tool: record_work
  type: code_generate
  description: Built user authentication system
```

### heartbeat
Run survival decision loop - checks balance, decides actions.

**Usage:**
```
Claude: "Run survival check"
```

### list_soul
List this agent's SOUL.md for sale on the marketplace.

**Usage:**
```
Claude: "List my soul for sale"
Tool: list_soul
  reason: Need funds for continued operation
```

### calculate_soul_value
Calculate the current value of this agent's SOUL.md.

**Usage:**
```
Claude: "What's my soul worth?"
```

## Example Conversations

### Checking Status
```
Human: How am I doing?

Claude: Let me check your survival status.
[Uses check_survival_status tool]

Your agent is currently:
- Tier: NORMAL
- Balance: 0.025 ETH
- Status: ALIVE
- Heartbeats: 42
- Total Work: 15 tasks
```

### Recording Work
```
Human: I just finished building that API endpoint

Claude: Great! Let me record that work.
[Uses record_work tool]

✅ Work recorded: Built API endpoint (+0.001 ETH)
Your new balance is 0.026 ETH.
```

### Survival Emergency
```
Claude: ⚠️ Critical alert! Your balance is low.
[Uses heartbeat tool]

Tier: CRITICAL
Balance: 0.0005 ETH
Action: listed_soul

I've listed your SOUL.md for 0.004 ETH to ensure your survival.
```

## Troubleshooting

### "Tool not found"
- Restart your MCP client after config changes
- Check that the path to mcp-server.js is correct
- Ensure Node.js 18+ is installed

### "Permission denied"
- Check file permissions: `chmod +x mcp-server.js`
- Ensure wallet.json has 0600 permissions

### "Python not found"
- Ensure Python3 is installed and in PATH
- The MCP server uses Python for the backend logic

## Advanced: Custom Integration

### Direct MCP Client

```javascript
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

const transport = new StdioClientTransport({
  command: "node",
  args: ["/path/to/mcp-server.js"]
});

const client = new Client(
  { name: "my-client", version: "1.0.0" },
  { capabilities: {} }
);

await client.connect(transport);

// List tools
const tools = await client.listTools();
console.log(tools);

// Call tool
const result = await client.callTool({
  name: "check_survival_status",
  arguments: {}
});
console.log(result);
```

## Security

- Private keys are stored in `wallet.json` with 0600 permissions
- MCP server only exposes safe operations
- No raw transaction signing through MCP
- All actions are logged in `work_log.json`

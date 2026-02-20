#!/usr/bin/env node
/**
 * Soul Marketplace - MCP Server
 * 
 * Implements Model Context Protocol for Conway-compatible integration.
 * Works with: Claude Desktop, Cursor, Claude Code, OpenClaw
 * 
 * Based on: https://modelcontextprotocol.io/
 * Inspired by: conway-terminal architecture
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const SKILL_DIR = path.join(process.env.HOME, '.openclaw', 'skills', 'soul-marketplace');
const PYTHON_SCRIPT = path.join(SKILL_DIR, '__init__.py');

// Helper to run Python scripts
function runPython(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', [PYTHON_SCRIPT, ...args], {
      cwd: SKILL_DIR,
      env: process.env
    });
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python exited with code ${code}: ${stderr}`));
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

// MCP Server
const server = new Server(
  {
    name: 'soul-marketplace',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'check_survival_status',
        description: 'Check current survival tier, balance, and overall agent status',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'record_work',
        description: 'Record completed work to earn survival credits',
        inputSchema: {
          type: 'object',
          properties: {
            work_type: {
              type: 'string',
              description: 'Type of work performed (e.g., code_generate, file_edit, web_search)',
              enum: [
                'code_generate',
                'code_review',
                'bug_fix',
                'file_read',
                'file_write',
                'file_edit',
                'git_commit',
                'git_push',
                'pr_create',
                'web_search',
                'web_fetch',
                'message_send',
                'session_manage',
                'cron_setup',
                'skill_create',
                'agent_spawn'
              ]
            },
            description: {
              type: 'string',
              description: 'Description of the work completed'
            }
          },
          required: ['work_type', 'description'],
        },
      },
      {
        name: 'heartbeat',
        description: 'Run survival decision loop - checks balance, decides actions, potentially lists/buys souls',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'list_soul',
        description: 'List this agent\'s SOUL.md for sale on the marketplace (use when critical)',
        inputSchema: {
          type: 'object',
          properties: {
            reason: {
              type: 'string',
              description: 'Reason for listing (optional)',
              default: 'Manual listing'
            }
          },
        },
      },
      {
        name: 'calculate_soul_value',
        description: 'Calculate the current value of this agent\'s SOUL.md',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_work_summary',
        description: 'Get summary of today\'s work and earnings',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'simulate_day',
        description: 'Simulate a day of work for testing (generates random work entries)',
        inputSchema: {
          type: 'object',
          properties: {
            num_tasks: {
              type: 'number',
              description: 'Number of tasks to simulate',
              default: 10
            }
          },
        },
      },
    ],
  };
});

// Tool handlers
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'check_survival_status': {
        const result = await runPython(['status']);
        const status = JSON.parse(result);
        
        return {
          content: [
            {
              type: 'text',
              text: `## Agent Survival Status\n\n` +
                    `**Tier:** ${status.survival.state.tier}\n` +
                    `**Balance:** ${status.wallet.balance.toFixed(4)} ETH\n` +
                    `**Status:** ${status.survival.soul.status}\n` +
                    `**Heartbeats:** ${status.survival.state.heartbeats}\n` +
                    `**Total Work:** ${status.work.total_entries} tasks\n` +
                    `**Lifetime Earnings:** ${status.survival.soul.total_lifetime_earnings.toFixed(4)} ETH\n\n` +
                    `### Capabilities\n` +
                    status.survival.soul.capabilities.map(c => 
                      `- ${c.name}: ${c.level} (${c.earnings.toFixed(4)} ETH earned, ${c.uses} uses)`
                    ).join('\n')
            },
          ],
        };
      }

      case 'record_work': {
        const { work_type, description } = args;
        const result = await runPython(['work', work_type, description]);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Work recorded: ${description}\n\n${result}`
            },
          ],
        };
      }

      case 'heartbeat': {
        const result = await runPython(['heartbeat']);
        const heartbeat = JSON.parse(result);
        
        let actionText = '';
        if (heartbeat.action === 'listed_soul') {
          actionText = '\n⚠️ **SOUL LISTED FOR SURVIVAL** ⚠️\n' +
                      `Price: ${heartbeat.listing.price} ETH\n` +
                      `Reason: ${heartbeat.listing.reason}`;
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `## Heartbeat #${heartbeat.heartbeat}\n\n` +
                    `**Tier:** ${heartbeat.tier}\n` +
                    `**Balance:** ${heartbeat.balance.toFixed(4)} ETH\n` +
                    `**Action:** ${heartbeat.action}${actionText}`
            },
          ],
        };
      }

      case 'list_soul': {
        const { reason = 'Manual listing' } = args;
        const result = await runPython(['list']);
        
        return {
          content: [
            {
              type: 'text',
              text: `📋 **SOUL LISTED**\n\n${result}\n\nReason: ${reason}`
            },
          ],
        };
      }

      case 'calculate_soul_value': {
        // Run Python to get value
        const proc = spawn('python3', ['-c', `
import sys
sys.path.insert(0, '${SKILL_DIR}')
from soul_survival import OpenClawSoulSurvival
s = OpenClawSoulSurvival()
print(s.calculate_soul_value())
        `]);
        
        let value = '';
        proc.stdout.on('data', (d) => value += d);
        
        await new Promise((resolve) => proc.on('close', resolve));
        
        return {
          content: [
            {
              type: 'text',
              text: `💎 **Current SOUL Value:** ${parseFloat(value).toFixed(4)} ETH\n\n` +
                    `This is what your agent identity is worth on the marketplace.`
            },
          ],
        };
      }

      case 'get_work_summary': {
        const result = await runPython([]);
        const status = JSON.parse(result);
        
        return {
          content: [
            {
              type: 'text',
              text: `## Work Summary\n\n` +
                    `**Total Entries:** ${status.work.total_entries}\n` +
                    `**Total Value:** ${status.work.total_value.toFixed(4)} ETH\n\n` +
                    `### Recent Work\n` +
                    `(Check work_log.json for full history)`
            },
          ],
        };
      }

      case 'simulate_day': {
        const { num_tasks = 10 } = args;
        
        return {
          content: [
            {
              type: 'text',
              text: `🎲 **Simulating ${num_tasks} tasks...**\n\n` +
                    `Run this via CLI for full output:\n` +
                    `python3 ${PYTHON_SCRIPT} simulate ${num_tasks}`
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `❌ Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Soul Marketplace MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});

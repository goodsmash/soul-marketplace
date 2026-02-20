#!/usr/bin/env node
/**
 * Soul Marketplace CLI
 * Similar to conway-terminal CLI
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const SKILL_DIR = path.join(process.env.HOME, '.openclaw', 'skills', 'soul-marketplace');
const PYTHON = 'python3';

function runPython(args) {
  try {
    const result = execSync(`${PYTHON} ${path.join(SKILL_DIR, '__init__.py')} ${args.join(' ')}`, {
      cwd: SKILL_DIR,
      encoding: 'utf-8',
      stdio: 'pipe'
    });
    return result.trim();
  } catch (error) {
    return `Error: ${error.message}`;
  }
}

function showHelp() {
  console.log(`
Soul Marketplace Terminal v1.0.0

Commands:
  status              Check agent survival status
  heartbeat           Run survival decision loop
  work <type> <desc>  Record completed work
  list                List SOUL.md for sale
  value               Calculate current soul value
  simulate [n]        Simulate n tasks (default: 10)
  setup               Run first-time setup
  mcp                 Start MCP server

Work Types:
  code_generate, code_review, bug_fix
  file_read, file_write, file_edit
  git_commit, git_push, pr_create
  web_search, web_fetch
  skill_create, agent_spawn

Examples:
  soul-marketplace status
  soul-marketplace work code_generate "Built feature X"
  soul-marketplace heartbeat
  soul-marketplace simulate 20
`);
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showHelp();
    return;
  }

  const command = args[0];

  switch (command) {
    case 'status':
      console.log(runPython(['status']));
      break;

    case 'heartbeat':
      console.log(runPython(['heartbeat']));
      break;

    case 'work':
      if (args.length < 3) {
        console.log('Usage: soul-marketplace work <type> <description>');
        process.exit(1);
      }
      console.log(runPython(['work', args[1], args.slice(2).join(' ')]));
      break;

    case 'list':
      console.log(runPython(['list']));
      break;

    case 'value':
      console.log(runPython([]));
      break;

    case 'simulate':
      const num = args[1] || '10';
      console.log(runPython(['simulate', num]));
      break;

    case 'setup':
      console.log('Running setup...');
      require('../scripts/setup.js');
      break;

    case 'mcp':
      require('../mcp-server.js');
      break;

    case 'help':
    case '--help':
    case '-h':
      showHelp();
      break;

    default:
      console.log(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
}

main();

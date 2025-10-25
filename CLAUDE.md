# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code marketplace repository that contains custom agents, commands, and hooks. The repository structure follows the Claude Code plugin marketplace format with:

- `.claude-plugin/marketplace.json` - Marketplace configuration
- `plugin/` - Main plugin directory containing all custom agents and commands

## Repository Structure

```
personal-marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── agents/           # Custom agent definitions
    ├── commands/         # Custom slash commands
    └── hooks/            # Auto-formatting hooks
        ├── hooks.json         # Hook configuration
        ├── auto-format.sh     # Formatting script
        └── README.md          # Hook documentation
```

## Agent Architecture

All agents are defined in `plugin/agents/` as Markdown files with YAML frontmatter. Each agent has:

- **name**: Agent identifier
- **description**: When/how to use the agent (may include usage examples)
- **tools**: List of available tools the agent can use
- **model**: AI model to use (sonnet/haiku)
- **color**: Terminal display color

### Available Custom Agents

1. **code-reviewer** (`code-reviewer.md`)
   - Uses Haiku model
   - Reviews code for quality, security, and maintainability
   - Must be run after any code changes (Edit/Write/MultiEdit)
   - Provides PASS/FAIL verdict with severity-categorized issues
   - Constructs proper GitLab/GitHub file links for MR/PR comments
   - Reports only issues with ≥80% confidence score

2. **software-architect** (`software-architect.md`)
   - Uses Haiku model
   - Evaluates high-level architecture and design patterns
   - Should run in parallel with code-reviewer for non-trivial changes
   - Assesses scalability, component design, and technical debt

3. **docs** (`docs.md`)
   - Uses Haiku model
   - Manages all documentation in `.docs/` directory
   - Runs after code-reviewer/software-architect approval
   - Maintains README, CHANGELOG, API docs, architecture docs

4. **librarian** (`librarian.md`)
   - Uses Haiku model
   - Fetches up-to-date documentation using Context7 MCP
   - Should be used immediately when documentation is needed
   - Never use WebFetch/WebSearch for documentation - always use librarian

5. **web-qa** (`web-qa.md`)
   - Uses Haiku model
   - Manual QA testing for web applications
   - Uses chrome-devtools MCP for browser automation
   - Tests functionality, responsiveness, performance, accessibility

6. **dbadmin** (`dbadmin.md`)
   - Uses Sonnet model
   - Handles all database operations via dbhub MCP
   - Query writing, schema design, optimization, migrations
   - Discovers available database connections via MCP

7. **mobile-dev** (`mobile-dev.md`)
   - Uses Sonnet model
   - Expert for Flutter and React Native development
   - Platform-specific knowledge for iOS/Android

## Custom Slash Commands

Commands are defined in `plugin/commands/` as Markdown files.

### `/pr` Command (`pr.md`)

Creates pull requests (GitHub) or merge requests (GitLab) with standardized format:

- Detects platform automatically (gh vs glab)
- Extracts task ID from branch name
- Title format: `TASK-123: Description` or `feat/fix/chore: description`
- Description includes `Closes: TASK-ID` when applicable
- ALWAYS runs `--help` first to check current CLI syntax

### `/code-review` Command (`code-review.md`)

Delegates to code-reviewer and software-architect agents:

- Runs both agents in parallel by default
- Analyzes existing MR/PR comments if URL provided
- Constructs proper file links with line numbers
- Asks before posting review comment to MR/PR
- Uses structured comment template with severity sections

## Auto-Formatting Hooks

The plugin includes automatic formatting hooks configured in `plugin/hooks/hooks.json` that trigger after any Edit/Write/MultiEdit operation using the `PostToolUse` event:

### Supported Languages and Tools

| Language                  | Formatters                     | Extensions                             |
| ------------------------- | ------------------------------ | -------------------------------------- |
| JavaScript/TypeScript/Vue | Prettier → ESLint              | .js, .jsx, .ts, .tsx, .vue, .mjs, .cjs |
| Python                    | Black → isort                  | .py                                    |
| Rust                      | rustfmt                        | .rs                                    |
| Go                        | gofmt → goimports              | .go                                    |
| Ruby                      | RuboCop                        | .rb                                    |
| PHP                       | PHP-CS-Fixer                   | .php                                   |
| Java                      | google-java-format             | .java                                  |
| CSS/SCSS/LESS             | Prettier                       | .css, .scss, .sass, .less              |
| HTML                      | Prettier                       | .html, .htm                            |
| JSON                      | Prettier                       | .json                                  |
| YAML                      | Prettier                       | .yml, .yaml                            |
| Markdown                  | Prettier                       | .md, .markdown                         |
| Dart                      | dart format                    | .dart                                  |
| Swift                     | swift-format                   | .swift                                 |
| Kotlin                    | ktlint                         | .kt                                    |
| SQL                       | sqlfluff (fallback: pg_format) | .sql                                   |

### Hook Configuration

The plugin includes two hooks in `hooks.json`:

**1. PostToolUse Hook - Auto-formatting:**

```json
{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/auto-format.sh"
    }
  ]
}
```

Runs after every edit to format code silently.

**2. Stop Hook - Code Review Trigger:**

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-code-review.sh"
    }
  ]
}
```

Runs when Claude finishes responding. If code changes are detected via `git diff`, it prevents stopping and prompts Claude to run the `code-reviewer` agent. This ensures reviews happen after feature completion, not after every individual edit.

### Hook Behavior

- Triggers automatically after `Edit`, `Write`, or `MultiEdit` tool usage
- Receives tool input via `$HOOK_INPUT` environment variable as JSON
- Extracts file path using `jq`: `$(echo "$HOOK_INPUT" | jq -r '.tool_input.file_path')`
- All formatter commands use `2>/dev/null || true` to fail silently if tools aren't installed
- Extension matching uses shell case patterns
- Multiple formatters run sequentially for the same language when applicable
- Script exits with status 0 to allow the tool operation to succeed regardless of formatting result

### Installing Formatters

Hooks will silently skip if formatters aren't installed. Install as needed:

```bash
# JavaScript/TypeScript
npm install -g prettier eslint

# Python
pip install black isort

# Rust (comes with rustup)
rustup component add rustfmt

# Go
go install golang.org/x/tools/cmd/goimports@latest

# And so on for other languages...
```

## Development Workflow

### When Modifying Agents

1. Edit agent Markdown files in `plugin/agents/`
2. Frontmatter format:
   ```yaml
   ---
   name: agent-name
   description: When to use this agent
   tools: List, Of, Tools
   model: sonnet|haiku
   color: colorname
   ---
   ```
3. Agent body contains full system prompt with instructions

### When Modifying Commands

1. Edit command Markdown files in `plugin/commands/`
2. Commands use `$ARGUMENTS` variable for user input
3. Commands should delegate to agents when appropriate

### Git Platform Integration

This repository heavily integrates with GitLab and GitHub:

- Use `glab` CLI for GitLab operations
- Use `gh` CLI for GitHub operations
- Always run `--help` before using CLI commands (they update frequently)
- Commit messages follow gitflow conventions or task ID patterns

## Key Principles

1. **Agent Delegation**: Main assistant should delegate specialized tasks to appropriate agents
2. **Parallel Execution**: Run code-reviewer and software-architect in parallel for efficiency
3. **No Comments in Code**: Project standard prohibits code comments in all generated code
4. **Confidence Scoring**: Code-reviewer only reports issues with ≥80% confidence
5. **MCP Integration**: Leverage Context7 (librarian), chrome-devtools (web-qa), and dbhub (dbadmin) MCPs
6. **Documentation Structure**: All docs in `.docs/` following specific hierarchy
7. **Auto-Formatting**: Hooks automatically format code after edits (fails silently if tools not installed)

## Testing and Quality

- code-reviewer enforces DRY, KISS, SOLID, YAGNI principles
- software-architect validates architectural soundness
- web-qa performs manual browser testing with chrome-devtools
- All agents provide structured output with severity levels

## Important Notes

- Agents use different models based on complexity (Sonnet for complex tasks, Haiku for reviews)
- CLI commands (gh/glab) must always verify syntax with --help due to frequent updates
- File links in MR/PR comments must use commit SHA if branch contains special characters
- docs agent maintains separate `.docs/` directory for all project docs

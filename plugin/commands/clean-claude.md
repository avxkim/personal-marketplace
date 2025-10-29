---
description: Clean Claude Code cache, logs, and conversation history to free disk space
argument-hint: "[status|gentle|deep|projects|transcripts|dry-run]"
---

Intelligently cleans Claude Code data with safety checks and multiple cleanup modes.

python3 ${CLAUDE_PLUGIN_ROOT}/commands/scripts/clean_claude.py $ARGUMENTS

**Arguments**:

- (no arguments) - Preview what would be deleted (same as dry-run)
- `status` - Display detailed storage breakdown without cleaning
- `dry-run` - Preview what would be deleted without making changes
- `gentle` - Clear cache directories (debug logs, file-history)
- `deep` - Also clear shell-snapshots, todos
- `projects` - Clean project settings from ~/.claude.json
- `transcripts` - Clean old conversation transcripts by age
- `all` - Full cleanup (requires confirmation)

**Examples**:

```bash
/clean-claude              # Preview cleanup (default)
/clean-claude status       # View storage usage
/clean-claude dry-run      # Preview cleanup (explicit)
/clean-claude gentle       # Quick cache cleanup (~158MB)
/clean-claude deep         # Aggressive cache cleanup (~170MB)
/clean-claude projects     # Clean dead project settings (~40MB)
/clean-claude transcripts  # Clean old conversations (age-based)
```

**Safety Features**:

- Dry-run mode to preview all changes
- Age-based deletion (preserves recent data)
- Automatic backups before modifying ~/.claude.json
- Validates JSON integrity after changes
- Per-project analysis before deletion

**What Gets Cleaned**:

| Data Type        | Location                  | Gentle | Deep | Projects | Transcripts | Safe?                       |
| ---------------- | ------------------------- | ------ | ---- | -------- | ----------- | --------------------------- |
| Debug logs       | ~/.claude/debug           | ✓      | ✓    |          |             | ✓ Regenerates               |
| File history     | ~/.claude/file-history    | ✓      | ✓    |          |             | ⚠️ Loses undo               |
| Shell snapshots  | ~/.claude/shell-snapshots |        | ✓    |          |             | ✓ Session only              |
| Todos            | ~/.claude/todos           |        | ✓    |          |             | ⚠️ Loses tasks              |
| Project settings | ~/.claude.json            |        |      | ✓        |             | ⚠️ Loses per-project config |
| Conversations    | ~/.claude/projects/\*     |        |      |          | ✓           | ⚠️ Loses history            |

**Storage Overview** (typical sizes):

- `~/.claude.json` - 41MB (project settings, history)
- `~/.claude/projects/` - 490MB (conversation transcripts)
- `~/.claude/debug/` - 138MB (debug logs)
- `~/.claude/file-history/` - 15MB (file change tracking)
- Other caches - ~12MB

**Integration**:

- Respects `cleanupPeriodDays` setting from settings.json
- Works with `/compact` command (session context vs disk cleanup)
- Identifies deleted project directories automatically

**Related Commands**:

- `/compact` - Reduce active session context size (in-memory)
- Settings: `cleanupPeriodDays` - Auto-cleanup threshold (default: 30 days)

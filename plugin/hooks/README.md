# Auto-Formatting Hooks

This directory contains hooks for automatically formatting code after Edit/Write/MultiEdit operations.

## Plugin-Based Hooks

This plugin includes two types of hooks that are automatically loaded when the plugin is installed:

### 1. Auto-Formatting Hook (PostToolUse)

Runs after every `Edit`, `Write`, or `MultiEdit` operation to format code:

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

This hook silently formats code based on file extension.

### 2. Code Review Hook (Stop)

Runs when Claude finishes responding. If code changes are detected (via `git diff`), it prevents Claude from stopping and prompts to run the `code-reviewer` agent:

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

**How it works:**
1. Checks if there are any uncommitted changes (`git diff`)
2. If changes found, returns `"continue": true` to prevent stopping
3. Displays message prompting Claude to run code-reviewer agent
4. If no changes, allows Claude to stop normally

This ensures code reviews happen after completing features, not after every individual edit.

## Supported Languages

The hook automatically formats files based on extension:

- **JavaScript/TypeScript/Vue**: Prettier + ESLint (.js, .jsx, .ts, .tsx, .vue, .mjs, .cjs)
- **Python**: Black + isort (.py)
- **Rust**: rustfmt (.rs)
- **Go**: gofmt + goimports (.go)
- **Ruby**: RuboCop (.rb)
- **PHP**: PHP-CS-Fixer (.php)
- **Java**: google-java-format (.java)
- **CSS/SCSS/LESS**: Prettier (.css, .scss, .sass, .less)
- **HTML**: Prettier (.html, .htm)
- **JSON**: Prettier (.json)
- **YAML**: Prettier (.yml, .yaml)
- **Markdown**: Prettier (.md, .markdown)
- **Dart**: dart format (.dart)
- **Swift**: swift-format (.swift)
- **Kotlin**: ktlint (.kt)
- **SQL**: sqlfluff or pg_format (.sql)

## How It Works

1. Hook triggers on `PostToolUse` event for Edit/Write/MultiEdit tools
2. Extracts file path from `$HOOK_INPUT` JSON
3. Matches file extension and runs appropriate formatter(s)
4. Fails silently if formatters aren't installed
5. Always exits 0 to not block the tool operation

## Installing Formatters

```bash
# JavaScript/TypeScript
npm install -g prettier eslint

# Python
pip install black isort

# Rust
rustup component add rustfmt

# Go
go install golang.org/x/tools/cmd/goimports@latest

# Ruby
gem install rubocop

# PHP
composer global require friendsofphp/php-cs-fixer

# Java
brew install google-java-format

# Dart (comes with Flutter)
flutter pub global activate dart_style

# Swift
brew install swift-format

# Kotlin
brew install ktlint

# SQL
pip install sqlfluff
brew install pgformatter
```

## Customization

Edit `auto-format.sh` to:
- Add new languages
- Change formatter order
- Add/remove file extensions
- Modify formatter flags

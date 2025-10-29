#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class ClaudeConfigCleaner:
    def __init__(self):
        self.home = Path.home()
        self.claude_dir = self.home / ".claude"
        self.claude_json = self.home / ".claude.json"
        self.settings_file = self.claude_dir / "settings.json"
        self.projects_dir = self.claude_dir / "projects"
        self.backup_dir = self.claude_dir / "backups"
        self.dry_run = False

    def validate_paths(self) -> bool:
        if not self.claude_dir.exists():
            print(f"Error: {self.claude_dir} does not exist.")
            print("Claude Code may not be installed or initialized.")
            return False

        if not self.claude_dir.is_dir():
            print(f"Error: {self.claude_dir} is not a directory.")
            return False

        return True

    def get_size(self, path: Path) -> int:
        if not path.exists():
            return 0
        if path.is_file():
            try:
                return path.stat().st_size
            except:
                return 0

        result = subprocess.run(
            ['du', '-sk', str(path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return int(result.stdout.split()[0]) * 1024

        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except:
                        pass
        except PermissionError:
            pass
        return total

    def format_size(self, size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"

    def get_cleanup_period_days(self) -> int:
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                return settings.get('cleanupPeriodDays', 30)
        except:
            pass
        return 30

    def get_storage_breakdown(self) -> Dict[str, int]:
        breakdown = {
            "claude_json": self.get_size(self.claude_json),
            "settings_json": self.get_size(self.settings_file),
            "projects_transcripts": self.get_size(self.projects_dir),
            "debug": self.get_size(self.claude_dir / "debug"),
            "file_history": self.get_size(self.claude_dir / "file-history"),
            "shell_snapshots": self.get_size(self.claude_dir / "shell-snapshots"),
            "todos": self.get_size(self.claude_dir / "todos"),
            "session_env": self.get_size(self.claude_dir / "session-env"),
            "history": self.get_size(self.claude_dir / "history.jsonl"),
        }

        known_size = sum(breakdown.values()) + self.get_size(self.backup_dir)
        total_size = self.get_size(self.claude_dir) + breakdown["claude_json"]
        breakdown["other"] = max(0, total_size - known_size)
        breakdown["total"] = total_size - self.get_size(self.backup_dir)

        return breakdown

    def display_storage(self, detailed: bool = False):
        print("\n" + "=" * 60)
        print("Claude Code Storage Analysis")
        print("=" * 60 + "\n")

        breakdown = self.get_storage_breakdown()
        cleanup_days = self.get_cleanup_period_days()

        print("Storage Breakdown:")
        print(f"  ~/.claude.json:            {self.format_size(breakdown['claude_json']):>10}  (project settings)")
        print(f"  ~/.claude/projects:        {self.format_size(breakdown['projects_transcripts']):>10}  (conversation history)")
        print(f"  ~/.claude/debug:           {self.format_size(breakdown['debug']):>10}  (debug logs)")
        print(f"  ~/.claude/file-history:    {self.format_size(breakdown['file_history']):>10}  (file changes)")
        print(f"  ~/.claude/shell-snapshots: {self.format_size(breakdown['shell_snapshots']):>10}  (shell state)")
        print(f"  ~/.claude/todos:           {self.format_size(breakdown['todos']):>10}  (task tracking)")
        print(f"  ~/.claude/session-env:     {self.format_size(breakdown['session_env']):>10}  (environment)")
        print(f"  ~/.claude/history.jsonl:   {self.format_size(breakdown['history']):>10}  (event log)")
        print(f"  Other:                     {self.format_size(breakdown['other']):>10}")
        print("  " + "─" * 56)
        print(f"  Total:                     {self.format_size(breakdown['total']):>10}\n")

        print(f"Settings: cleanupPeriodDays = {cleanup_days} days\n")

        if detailed:
            self.show_project_details()
            self.show_transcript_details()

        return breakdown

    def show_project_details(self):
        if not self.claude_json.exists():
            return

        try:
            with open(self.claude_json, 'r') as f:
                data = json.load(f)

            projects = data.get('projects', {})
            if not projects:
                return

            print("Project Settings in ~/.claude.json:")

            project_sizes = []
            for project_path, project_data in projects.items():
                size = len(json.dumps(project_data))
                exists = Path(project_path).exists()
                project_sizes.append((project_path, size, exists))

            project_sizes.sort(key=lambda x: x[1], reverse=True)

            total_dead = 0
            dead_count = 0

            for i, (path, size, exists) in enumerate(project_sizes[:10], 1):
                status = "✓" if exists else "✗ DELETED"
                print(f"  [{i:2d}] {self.format_size(size):>10}  {status}  {path}")
                if not exists:
                    total_dead += size
                    dead_count += 1

            if len(project_sizes) > 10:
                print(f"  ... and {len(project_sizes) - 10} more projects\n")
            else:
                print()

            if dead_count > 0:
                print(f"  Dead projects (directory deleted): {dead_count}")
                print(f"  Reclaimable space: {self.format_size(total_dead)}\n")
        except Exception as e:
            print(f"  Error analyzing projects: {e}\n")

    def show_transcript_details(self):
        if not self.projects_dir.exists():
            return

        print("Conversation Transcripts in ~/.claude/projects:")

        project_sizes = []
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                size = self.get_size(project_dir)
                project_sizes.append((project_dir.name, size))

        project_sizes.sort(key=lambda x: x[1], reverse=True)

        for i, (name, size) in enumerate(project_sizes[:10], 1):
            print(f"  [{i:2d}] {self.format_size(size):>10}  {name}")

        if len(project_sizes) > 10:
            print(f"  ... and {len(project_sizes) - 10} more projects\n")
        else:
            print()

    def create_backup(self, description: str = "") -> Optional[Path]:
        if self.dry_run:
            print(f"[DRY RUN] Would create backup: {description}")
            return None

        if not self.claude_json.exists():
            return None

        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_file = self.backup_dir / f"claude.json.backup.{timestamp}"

        shutil.copy2(self.claude_json, backup_file)
        print(f"✓ Backup created: {backup_file.name}")

        backups = sorted(self.backup_dir.glob("claude.json.backup.*"))
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                old_backup.unlink()
                print(f"  Removed old backup: {old_backup.name}")

        return backup_file

    def load_claude_json(self) -> dict:
        with open(self.claude_json, 'r') as f:
            return json.load(f)

    def save_claude_json(self, data: dict):
        if self.dry_run:
            print("[DRY RUN] Would save ~/.claude.json")
            return

        with open(self.claude_json, 'w') as f:
            json.dump(data, f, indent=2)

    def validate_json(self) -> bool:
        try:
            self.load_claude_json()
            return True
        except json.JSONDecodeError:
            return False

    def clean_cache_directories(self, include_extras: bool = False) -> Tuple[int, List[str]]:
        bytes_saved = 0
        removed = []

        dirs_to_clean = [
            (self.claude_dir / "debug", "Debug logs"),
            (self.claude_dir / "file-history", "File history"),
        ]

        if include_extras:
            dirs_to_clean.extend([
                (self.claude_dir / "shell-snapshots", "Shell snapshots"),
                (self.claude_dir / "todos", "Todos"),
            ])

        for dir_path, description in dirs_to_clean:
            if dir_path.exists():
                dir_size = self.get_size(dir_path)
                if dir_size > 0:
                    if self.dry_run:
                        removed.append(f"  • Would clear {description.lower()}: {self.format_size(dir_size)}")
                        bytes_saved += dir_size
                    else:
                        shutil.rmtree(dir_path)
                        dir_path.mkdir()
                        bytes_saved += dir_size
                        removed.append(f"  • Cleared {description.lower()}: {self.format_size(dir_size)}")

        if not removed:
            removed.append("  • Nothing to clean")

        return bytes_saved, removed

    def clean_dead_projects(self) -> Tuple[int, List[str]]:
        if not self.claude_json.exists():
            return 0, ["  • ~/.claude.json not found"]

        try:
            data = self.load_claude_json()
            projects = data.get('projects', {})

            dead_projects = []
            total_size = 0

            for project_path in list(projects.keys()):
                if not Path(project_path).exists():
                    size = len(json.dumps(projects[project_path]))
                    dead_projects.append((project_path, size))
                    total_size += size

                    if not self.dry_run:
                        del projects[project_path]

            if dead_projects:
                if not self.dry_run:
                    self.save_claude_json(data)
                    if not self.validate_json():
                        raise ValueError("JSON validation failed after cleanup")

                removed = []
                for path, size in dead_projects:
                    prefix = "Would remove" if self.dry_run else "Removed"
                    removed.append(f"  • {prefix} dead project: {path} ({self.format_size(size)})")

                return total_size, removed
            else:
                return 0, ["  • No dead projects found"]

        except Exception as e:
            return 0, [f"  • Error: {e}"]

    def clean_old_transcripts(self, days: int = None) -> Tuple[int, List[str]]:
        if days is None:
            days = self.get_cleanup_period_days()

        if not self.projects_dir.exists():
            return 0, ["  • No transcript directory found"]

        cutoff = datetime.now() - timedelta(days=days)
        bytes_saved = 0
        removed = []
        file_count = 0

        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            for transcript_file in project_dir.glob("*.jsonl"):
                try:
                    mtime = datetime.fromtimestamp(transcript_file.stat().st_mtime)
                    if mtime < cutoff:
                        size = transcript_file.stat().st_size

                        if self.dry_run:
                            bytes_saved += size
                            file_count += 1
                        else:
                            transcript_file.unlink()
                            bytes_saved += size
                            file_count += 1
                except Exception:
                    continue

        if file_count > 0:
            prefix = "Would remove" if self.dry_run else "Removed"
            removed.append(f"  • {prefix} {file_count} transcripts older than {days} days")
            removed.append(f"    Space freed: {self.format_size(bytes_saved)}")
        else:
            removed.append(f"  • No transcripts older than {days} days found")

        return bytes_saved, removed

    def show_dry_run_preview(self):
        print("\n" + "=" * 60)
        print("DRY RUN - Preview of Changes (No files will be modified)")
        print("=" * 60 + "\n")

        self.dry_run = True
        total_bytes = 0

        print("1. Cache Cleanup (Gentle):")
        bytes_saved, removed = self.clean_cache_directories(include_extras=False)
        total_bytes += bytes_saved
        for item in removed:
            print(item)
        print()

        print("2. Extra Cache Cleanup (Deep):")
        bytes_saved, removed = self.clean_cache_directories(include_extras=True)
        extra_bytes = bytes_saved - total_bytes
        total_bytes = bytes_saved
        if extra_bytes > 0:
            print(f"  • Additional savings: {self.format_size(extra_bytes)}")
        print()

        print("3. Dead Project Settings (Projects):")
        bytes_saved, removed = self.clean_dead_projects()
        total_bytes += bytes_saved
        for item in removed:
            print(item)
        print()

        print("4. Old Transcripts (Transcripts):")
        bytes_saved, removed = self.clean_old_transcripts()
        total_bytes += bytes_saved
        for item in removed:
            print(item)
        print()

        print("=" * 60)
        print(f"Total potential space savings: {self.format_size(total_bytes)}")
        print("=" * 60 + "\n")

        self.dry_run = False

    def show_menu(self):
        self.display_storage(detailed=False)

        print("Cleanup Options:")
        print("  [1] Gentle clean     - Clear debug logs, file-history (~158MB)")
        print("  [2] Deep clean       - Also clear shell-snapshots, todos (~170MB)")
        print("  [3] Projects clean   - Remove dead project settings from ~/.claude.json")
        print("  [4] Transcripts      - Clean old conversation files by age")
        print("  [5] All (Full clean) - All of the above (requires confirmation)")
        print("  [6] Dry-run preview  - Show what would be deleted")
        print("  [7] Detailed status  - Show per-project breakdown")
        print("  [8] Cancel\n")

        try:
            choice = input("Choose option [1-8]: ").strip()
            return choice
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return "8"

    def run(self, args: List[str]):
        if not self.validate_paths():
            return 1

        if len(args) == 0:
            self.show_dry_run_preview()
            return 0
        elif args[0] == "status":
            self.display_storage(detailed=False)
            return 0
        elif args[0] == "dry-run":
            self.show_dry_run_preview()
            return 0
        elif args[0] == "gentle":
            choice = "1"
        elif args[0] == "deep":
            choice = "2"
        elif args[0] == "projects":
            choice = "3"
        elif args[0] == "transcripts":
            choice = "4"
        elif args[0] == "all":
            choice = "5"
        elif args[0] == "detailed":
            self.display_storage(detailed=True)
            return 0
        else:
            print(f"Error: Unknown argument '{args[0]}'")
            print("Usage: /clean-claude [status|dry-run|gentle|deep|projects|transcripts|all|detailed]")
            return 1

        if choice == "1":
            print("\n" + "=" * 60)
            print("Gentle Clean - Cache Directories")
            print("=" * 60 + "\n")

            try:
                bytes_saved, removed = self.clean_cache_directories(include_extras=False)
                print("Cleaning complete:")
                for item in removed:
                    print(item)
                print(f"\n✓ Space freed: {self.format_size(bytes_saved)}\n")
            except Exception as e:
                print(f"\n✗ Error during cleanup: {e}\n")
                return 1

        elif choice == "2":
            print("\n" + "=" * 60)
            print("Deep Clean - All Cache Directories")
            print("=" * 60 + "\n")
            print("This will remove debug logs, file-history, shell-snapshots, and todos.")
            confirm = input("Continue? [y/N]: ").strip().lower()
            if confirm != "y":
                print("Cancelled.")
                return 0

            try:
                bytes_saved, removed = self.clean_cache_directories(include_extras=True)
                print("\nCleaning complete:")
                for item in removed:
                    print(item)
                print(f"\n✓ Space freed: {self.format_size(bytes_saved)}\n")
            except Exception as e:
                print(f"\n✗ Error during cleanup: {e}\n")
                return 1

        elif choice == "3":
            print("\n" + "=" * 60)
            print("Projects Clean - Remove Dead Project Settings")
            print("=" * 60 + "\n")

            self.show_project_details()

            confirm = input("\nRemove project settings for deleted directories? [y/N]: ").strip().lower()
            if confirm != "y":
                print("Cancelled.")
                return 0

            self.create_backup("Before cleaning dead projects")

            try:
                bytes_saved, removed = self.clean_dead_projects()
                print("\nCleaning complete:")
                for item in removed:
                    print(item)
                print(f"\n✓ Space freed in ~/.claude.json: {self.format_size(bytes_saved)}\n")
            except Exception as e:
                print(f"\n✗ Error during cleanup: {e}\n")
                return 1

        elif choice == "4":
            print("\n" + "=" * 60)
            print("Transcripts Clean - Remove Old Conversations")
            print("=" * 60 + "\n")

            cleanup_days = self.get_cleanup_period_days()
            print(f"Current setting: cleanupPeriodDays = {cleanup_days} days\n")

            response = input(f"Remove transcripts older than {cleanup_days} days? [Y/n]: ").strip().lower()
            if response == 'n':
                print("Cancelled.")
                return 0

            try:
                bytes_saved, removed = self.clean_old_transcripts()
                print("\nCleaning complete:")
                for item in removed:
                    print(item)
                print(f"\n✓ Total space freed: {self.format_size(bytes_saved)}\n")
            except Exception as e:
                print(f"\n✗ Error during cleanup: {e}\n")
                return 1

        elif choice == "5":
            print("\n" + "=" * 60)
            print("Full Clean - All Cleanup Operations")
            print("=" * 60 + "\n")
            print("⚠️  WARNING: This will perform all cleanup operations:")
            print("   - Clear all cache directories")
            print("   - Remove dead project settings")
            print("   - Delete old conversation transcripts")
            print()

            confirm = input("Are you sure? Type 'yes' to confirm: ").strip()
            if confirm != "yes":
                print("Cancelled.")
                return 0

            self.create_backup("Before full cleanup")

            total_bytes = 0

            print("\n1. Cleaning cache directories...")
            bytes_saved, removed = self.clean_cache_directories(include_extras=True)
            total_bytes += bytes_saved
            for item in removed:
                print(item)

            print("\n2. Cleaning dead projects...")
            bytes_saved, removed = self.clean_dead_projects()
            total_bytes += bytes_saved
            for item in removed:
                print(item)

            print("\n3. Cleaning old transcripts...")
            bytes_saved, removed = self.clean_old_transcripts()
            total_bytes += bytes_saved
            for item in removed:
                print(item)

            print("\n" + "=" * 60)
            print(f"✓ Full cleanup complete! Total space freed: {self.format_size(total_bytes)}")
            print("=" * 60 + "\n")

        elif choice == "6":
            self.show_dry_run_preview()

        elif choice == "7":
            self.display_storage(detailed=True)

        elif choice == "8":
            print("\nCancelled.\n")
            return 0

        else:
            print("\nInvalid choice.\n")
            return 1

        return 0


if __name__ == "__main__":
    cleaner = ClaudeConfigCleaner()
    sys.exit(cleaner.run(sys.argv[1:]))

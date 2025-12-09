"""
Diff parser for extracting meaningful code changes.
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from unidiff import PatchSet
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeHunk:
    """Represents a hunk of code changes."""
    file_path: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    added_lines: List[Tuple[int, str]]  # (line_number, content)
    removed_lines: List[Tuple[int, str]]
    context_lines: List[Tuple[int, str]]


class DiffParser:
    """Parse and analyze diffs."""

    @staticmethod
    def parse_patch(patch_text: str) -> List[CodeHunk]:
        """
        Parse a unified diff patch.

        Args:
            patch_text: Unified diff format text

        Returns:
            List of CodeHunk objects
        """
        if not patch_text:
            return []

        try:
            patch_set = PatchSet(patch_text)
            hunks = []

            for patched_file in patch_set:
                file_path = patched_file.path

                for hunk in patched_file:
                    added_lines = []
                    removed_lines = []
                    context_lines = []

                    for line in hunk:
                        if line.is_added:
                            added_lines.append((line.target_line_no, line.value))
                        elif line.is_removed:
                            removed_lines.append((line.source_line_no, line.value))
                        else:  # context
                            context_lines.append((line.target_line_no, line.value))

                    code_hunk = CodeHunk(
                        file_path=file_path,
                        old_start=hunk.source_start,
                        old_count=hunk.source_length,
                        new_start=hunk.target_start,
                        new_count=hunk.target_length,
                        added_lines=added_lines,
                        removed_lines=removed_lines,
                        context_lines=context_lines
                    )
                    hunks.append(code_hunk)

            return hunks

        except Exception as e:
            logger.error(f"Error parsing patch: {e}")
            return []

    @staticmethod
    def extract_functions(hunks: List[CodeHunk]) -> Dict[str, List[str]]:
        """
        Extract function/method names from changed code.

        Args:
            hunks: List of code hunks

        Returns:
            Dictionary mapping file paths to function names
        """
        functions_by_file = {}

        # Patterns for different languages
        patterns = {
            'python': r'^\s*def\s+(\w+)\s*\(',
            'javascript': r'^\s*(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()',
            'java': r'^\s*(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\(',
            'go': r'^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(',
        }

        for hunk in hunks:
            file_path = hunk.file_path
            extension = file_path.split('.')[-1] if '.' in file_path else ''

            # Determine language
            lang_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'javascript',
                'java': 'java',
                'go': 'go'
            }
            language = lang_map.get(extension)

            if not language or language not in patterns:
                continue

            pattern = patterns[language]
            functions = set()

            # Check added lines for function definitions
            for _, line_content in hunk.added_lines + hunk.context_lines:
                match = re.match(pattern, line_content)
                if match:
                    # Get first non-None group
                    func_name = next((g for g in match.groups() if g), None)
                    if func_name:
                        functions.add(func_name)

            if functions:
                if file_path not in functions_by_file:
                    functions_by_file[file_path] = []
                functions_by_file[file_path].extend(functions)

        return functions_by_file

    @staticmethod
    def get_change_summary(hunks: List[CodeHunk]) -> Dict[str, int]:
        """
        Get summary statistics of changes.

        Args:
            hunks: List of code hunks

        Returns:
            Dictionary with change statistics
        """
        total_added = 0
        total_removed = 0
        files_changed = set()

        for hunk in hunks:
            total_added += len(hunk.added_lines)
            total_removed += len(hunk.removed_lines)
            files_changed.add(hunk.file_path)

        return {
            'total_added': total_added,
            'total_removed': total_removed,
            'files_changed': len(files_changed),
            'net_change': total_added - total_removed
        }

    @staticmethod
    def get_file_extensions(hunks: List[CodeHunk]) -> Dict[str, int]:
        """
        Get count of files by extension.

        Args:
            hunks: List of code hunks

        Returns:
            Dictionary mapping extensions to counts
        """
        extensions = {}

        for hunk in hunks:
            file_path = hunk.file_path
            ext = file_path.split('.')[-1] if '.' in file_path else 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1

        return extensions


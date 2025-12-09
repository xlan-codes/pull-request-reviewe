"""
Code analysis tools integration.
"""
import subprocess
import json
from typing import List, Dict, Any
import logging
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Wrapper for static code analysis tools."""

    def __init__(self):
        """Initialize code analyzer."""
        self.available_tools = self._check_available_tools()
        logger.info(f"Available analysis tools: {list(self.available_tools.keys())}")

    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which analysis tools are available."""
        tools = {}

        # Check for pylint
        try:
            subprocess.run(['pylint', '--version'], capture_output=True, check=True)
            tools['pylint'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['pylint'] = False

        # Check for flake8
        try:
            subprocess.run(['flake8', '--version'], capture_output=True, check=True)
            tools['flake8'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['flake8'] = False

        return tools

    def analyze_python_code(self, code: str, filename: str = "temp.py") -> Dict[str, Any]:
        """
        Analyze Python code for issues.

        Args:
            code: Python code to analyze
            filename: Filename for context

        Returns:
            Analysis results
        """
        issues = []

        # Write code to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run flake8 if available
            if self.available_tools.get('flake8'):
                try:
                    result = subprocess.run(
                        ['flake8', temp_path],
                        capture_output=True,
                        text=True
                    )

                    for line in result.stdout.splitlines():
                        if line.strip():
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                issues.append({
                                    'tool': 'flake8',
                                    'file': filename,
                                    'line': int(parts[1]) if parts[1].isdigit() else 0,
                                    'column': int(parts[2]) if parts[2].isdigit() else 0,
                                    'message': parts[3].strip(),
                                    'severity': 'warning'
                                })
                except Exception as e:
                    logger.debug(f"Flake8 analysis error: {e}")

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

        return {
            'filename': filename,
            'issues': issues,
            'tool_count': len([t for t in self.available_tools.values() if t])
        }

    def analyze_code(self, code: str, language: str, filename: str = "") -> Dict[str, Any]:
        """
        Analyze code based on language.

        Args:
            code: Code to analyze
            language: Programming language
            filename: Original filename

        Returns:
            Analysis results
        """
        filename = filename or f"temp.{self._get_extension(language)}"

        if language.lower() in ['python', 'py']:
            return self.analyze_python_code(code, filename)
        else:
            logger.warning(f"No analyzer available for {language}")
            return {
                'filename': filename,
                'issues': [],
                'tool_count': 0,
                'message': f'Analysis not available for {language}'
            }

    def _get_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'go': 'go',
            'ruby': 'rb',
            'php': 'php'
        }
        return extensions.get(language.lower(), 'txt')

    def get_tool_status(self) -> Dict[str, bool]:
        """Get status of all analysis tools."""
        return self.available_tools.copy()


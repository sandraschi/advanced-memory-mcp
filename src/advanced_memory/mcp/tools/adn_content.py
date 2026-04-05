"""Backward-compatible shim for the legacy adn_content tool module.

The canonical implementation now lives in content_manager.py, but some
scripts still import advanced_memory.mcp.tools.adn_content. Re-export
the main entrypoint so those imports continue to succeed.
"""

from .content_manager import adn_content, adn_corpus_qc, adn_note_ai, adn_notes

__all__ = ["adn_content", "adn_corpus_qc", "adn_note_ai", "adn_notes"]

"""Content generators for whimsical edit operations.

This module provides generators for special content types like Mermaid diagrams,
ASCII art, and classic memes like Kilroy.
"""

from datetime import datetime
from typing import Literal


def generate_mermaid_diagram(
    diagram_type: Literal["flowchart", "sequence", "gantt", "mindmap", "er"] = "flowchart",
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Generate a Mermaid diagram code block.

    This function generates Mermaid diagrams that can be rendered in HTML exports.
    When custom content is provided, it should be valid Mermaid syntax.

    MERMAID SYNTAX REFERENCE:
    -------------------------
    Flowcharts: graph TD\n    A[Label] --> B[Label]
    Sequence: sequenceDiagram\n    participant A\n    A->>B: Message
    Gantt: gantt\n    title Title\n    dateFormat YYYY-MM-DD\n    section S1\n    Task :done, id, start, end
    Mindmap: mindmap\n    root((Root))\n        Branch\n            Leaf
    ER: erDiagram\n    ENTITY1 ||--o{ ENTITY2 : "rel"\n    ENTITY1 { string id PK }

    Args:
        diagram_type: Type of Mermaid diagram to generate (flowchart, sequence, gantt, mindmap, er)
        title: Optional title for the diagram (displayed above diagram)
        content: Optional custom Mermaid content. If provided, uses this directly instead of template.
                 Must be valid Mermaid syntax. Examples:
                 - Flowchart: "graph TD\n    A[Start] --> B[End]"
                 - Sequence: "sequenceDiagram\n    participant U\n    participant S\n    U->>S: Request"
                 - Gantt: "gantt\n    title Timeline\n    dateFormat YYYY-MM-DD\n    section Phase1\n    Task :t1, 2024-01-01, 2024-01-15"
                 - Mindmap: "mindmap\n    root((Topic))\n        Branch1\n        Branch2"
                 - ER: "erDiagram\n    USER ||--o{ PROJECT : owns\n    USER { string id PK }"

    Returns:
        Markdown code block with Mermaid diagram (wrapped in ```mermaid ... ```)

    Examples:
        # Generate flowchart template
        generate_mermaid_diagram("flowchart", title="Process Flow")

        # Generate custom flowchart
        generate_mermaid_diagram(
            diagram_type="flowchart",
            content="graph LR\n    A[Start] --> B[Process]\n    B --> C[End]"
        )

        # Generate sequence diagram
        generate_mermaid_diagram(
            "sequence",
            content="sequenceDiagram\n    participant U as User\n    participant S as Server\n    U->>S: Login\n    S-->>U: Token"
        )
    """
    if content:
        # Use provided content directly
        mermaid_content = content
    else:
        # Generate template based on type
        if diagram_type == "flowchart":
            mermaid_content = """graph TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
    D --> F[End]
    E --> F"""
        elif diagram_type == "sequence":
            mermaid_content = """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hi Alice!"""
        elif diagram_type == "gantt":
            mermaid_content = """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Task 1           :done, t1, 2024-01-01, 2024-01-15
    Task 2           :active, t2, 2024-01-16, 2024-02-01
    section Phase 2
    Task 3           :t3, 2024-02-02, 2024-02-15"""
        elif diagram_type == "mindmap":
            mermaid_content = """mindmap
  root((Main Topic))
    Branch 1
      Leaf 1.1
      Leaf 1.2
    Branch 2
      Leaf 2.1
      Leaf 2.2"""
        elif diagram_type == "er":
            mermaid_content = """erDiagram
    ENTITY1 ||--o{ ENTITY2 : "relationship"
    ENTITY1 {
        string id PK
        string name
    }
    ENTITY2 {
        string id PK
        string entity1_id FK
    }"""
        else:
            mermaid_content = "graph TD\n    A --> B"

    result = "```mermaid\n"
    if title:
        result += f"---\ntitle: {title}\n---\n"
    result += mermaid_content
    result += "\n```"
    return result


def generate_ascii_art(
    art_type: Literal["cat", "dog", "robot", "heart", "star", "tree"] = "cat",
) -> str:
    """Generate ASCII art.

    Args:
        art_type: Type of ASCII art to generate

    Returns:
        ASCII art as a string
    """
    art_map = {
        "cat": """
 /\\_/\\
( o.o )
 > ^ <
""",
        "dog": """
    __
   /  \\
  |    |
  |    |
  |____|
   /  \\
  /    \\
""",
        "robot": """
  _____
 |     |
 | O O |
 |  ^  |
 | \\_/ |
 |_____|
""",
        "heart": """
  ***   ***
 ***** *****
 ***********
  *********
   *******
    *****
     ***
      *
""",
        "star": """
    *
   ***
  *****
   ***
    *
""",
        "tree": """
    *
   ***
  *****
 *******
   |||
   |||
""",
    }

    return art_map.get(art_type, art_map["cat"]).strip()


def generate_kilroy(message: str = "KILROY WAS HERE") -> str:
    """Generate the classic Kilroy ASCII art.

    Args:
        message: Custom message to display (default: "KILROY WAS HERE")

    Returns:
        Kilroy ASCII art with message
    """
    kilroy = f"""
    ___
   |   |
   |   |
   |___|
    | |
    | |
   /   \\
  |  O  |
  |     |
  |_____|
   |   |
   |   |
   |___|

{message}
"""
    return kilroy.strip()


def generate_kanban_board(
    columns: list[str] | None = None,
    title: str | None = None,
) -> str:
    """Generate a Kanban board using markdown table format.

    Follows standard markdown table format for Kanban boards.
    Columns represent workflow stages (e.g., To Do, In Progress, Done).
    Tasks can be added as bullet points in each column.

    Args:
        columns: List of column names (default: ["To Do", "In Progress", "Done"])
        title: Optional board title

    Returns:
        Markdown Kanban board as a table

    Example:
        generate_kanban_board(["Backlog", "In Progress", "Review", "Done"], "Project Tasks")
    """
    if columns is None:
        columns = ["To Do", "In Progress", "Done"]

    result = ""
    if title:
        result += f"## {title}\n\n"

    # Create markdown table header
    header = "| " + " | ".join(columns) + " |\n"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"
    result += header + separator

    # Add empty row for tasks (users can add tasks as bullet points)
    empty_row = "| " + " | ".join(["- "] * len(columns)) + " |\n"
    result += empty_row

    result += "\n**Usage**: Add tasks as bullet points in each column cell.\n"
    result += "\n**Example**:\n"
    result += "```markdown\n"
    result += "| To Do | In Progress | Done |\n"
    result += "|-------|-------------|------|\n"
    result += "| - Task 1<br>- Task 2 | - Task 3 | - Completed Task |\n"
    result += "```\n"

    return result


def generate_changelog(
    version: str = "Unreleased",
    date: str | None = None,
    project_name: str | None = None,
) -> str:
    """Generate a changelog entry following Keep a Changelog standard.

    Follows the Keep a Changelog format (https://keepachangelog.com/):
    - Semantic versioning (MAJOR.MINOR.PATCH)
    - Standardized change categories
    - Date-based organization
    - Clear, concise descriptions

    Args:
        version: Version number (e.g., "1.0.0", "Unreleased", "2.1.3")
        date: Release date in YYYY-MM-DD format (default: today or "Unreleased")
        project_name: Optional project name for header

    Returns:
        Markdown changelog entry following Keep a Changelog format

    Example:
        generate_changelog("1.2.0", "2024-01-15", "My Project")
    """
    if date is None:
        if version.lower() == "unreleased":
            date = "Unreleased"
        else:
            date = datetime.now().strftime("%Y-%m-%d")

    changelog = ""
    if project_name:
        changelog += f"# {project_name}\n\n"
        changelog += "All notable changes to this project will be documented in this file.\n\n"
        changelog += "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
        changelog += "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
        changelog += "---\n\n"

    changelog += f"## [{version}] - {date}\n\n"
    changelog += "### Added\n"
    changelog += "- New features and enhancements\n\n"
    changelog += "### Changed\n"
    changelog += "- Changes to existing functionality\n\n"
    changelog += "### Deprecated\n"
    changelog += "- Features that will be removed in future versions\n\n"
    changelog += "### Removed\n"
    changelog += "- Removed features\n\n"
    changelog += "### Fixed\n"
    changelog += "- Bug fixes\n\n"
    changelog += "### Security\n"
    changelog += "- Security vulnerability fixes\n"

    return changelog


def generate_whimsical_separator(
    style: Literal["dotted", "dashed", "stars", "arrows"] = "dotted",
) -> str:
    """Generate a whimsical markdown separator.

    Args:
        style: Style of separator

    Returns:
        Markdown separator line
    """
    separators = {
        "dotted": "---",
        "dashed": "- - - - - - - - - - - - - - - - - - - -",
        "stars": "✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧",
        "arrows": "→ → → → → → → → → → → → → → → → → → → →",
    }
    return separators.get(style, separators["dotted"])

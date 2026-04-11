"""Prefab UI components for Advanced Memory MCP.

This module defines high-fidelity UI components using the FastMCP 3.1 Prefab system.
Aesthetics leverage the SOTA 2026 'Glassmorphism' and 'Point Cloud' design patterns.
"""

from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Button,
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
    Column,
    Grid,
    Markdown,
    Mermaid,
    Page,
    Pages,
    Text,
)
from pydantic import BaseModel


class NoteMetadata(BaseModel):
    title: str
    permalink: str
    project: str
    created_at: str
    tags: list[str]
    type: str


def NoteViewer(content: str, metadata: NoteMetadata) -> PrefabApp:
    """Standard premium note viewer prefab."""
    return PrefabApp(
        title=f"Note: {metadata.title}",
        view=Pages(
            children=[
                Page(
                    title="Content",
                    children=[
                        Grid(
                            columns=[3, 1],
                            gap=4,
                            children=[
                                # Main Content Area
                                Card(
                                    css_class="pf-glass",
                                    children=[CardContent(children=[Markdown(content)])],
                                ),
                                # Sidebar Metadata
                                Column(
                                    gap=3,
                                    children=[
                                        Card(
                                            css_class="pf-outline",
                                            children=[
                                                CardHeader(children=[CardTitle("Metadata")]),
                                                CardContent(
                                                    children=[
                                                        Text(
                                                            f"**Project:** {metadata.project}",
                                                            size="xs",
                                                        ),
                                                        Text(
                                                            f"**Permalink:** `{metadata.permalink}`",
                                                            size="xs",
                                                        ),
                                                        Text(f"**Type:** {metadata.type}", size="xs"),
                                                        Text(
                                                            f"**Created:** {metadata.created_at}",
                                                            size="xs",
                                                        ),
                                                    ]
                                                ),
                                            ],
                                        ),
                                        Card(
                                            css_class="pf-outline",
                                            children=[
                                                CardHeader(children=[CardTitle("Tags")]),
                                                CardContent(
                                                    children=[
                                                        Text(
                                                            ", ".join([f"#{t}" for t in metadata.tags]),
                                                            color="cyan",
                                                        )
                                                    ]
                                                ),
                                            ],
                                        ),
                                        Button(
                                            label="Open in Webapp",
                                            icon="external-link",
                                            on_click=f"open_url:http://localhost:10744/note/{metadata.permalink}",
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ]
        ),
    )


def KnowledgeGraph(nodes: list[dict], edges: list[dict], title: str = "Research Graph") -> PrefabApp:
    """Interactive Knowledge Graph using Mermaid Flowchart."""
    # Convert nodes and edges to Mermaid flowchart syntax
    mermaid_lines = ["graph TD"]
    for node in nodes:
        node_id = node.get("id", "unknown")
        label = node.get("label") or node_id
        # Use different shapes based on node type if available
        mermaid_lines.append(f'    {node_id}["{label}"]')

    for edge in edges:
        from_node = edge.get("from") or edge.get("source")
        to_node = edge.get("to") or edge.get("target")
        label = edge.get("label", "")
        if label:
            mermaid_lines.append(f'    {from_node} -- "{label}" --> {to_node}')
        else:
            mermaid_lines.append(f"    {from_node} --> {to_node}")

    chart_def = "\n".join(mermaid_lines)

    return PrefabApp(
        title=title,
        view=Pages(
            children=[
                Page(
                    title="Graph",
                    children=[
                        Card(
                            css_class="pf-glass",
                            children=[CardContent(children=[Mermaid(chart=chart_def)])],
                        )
                    ],
                )
            ]
        ),
    )


def SearchExplorer(query: str, results: list[dict]) -> PrefabApp:
    """Rich interactive search results with quick-action cards."""
    return PrefabApp(
        title=f"Explorer: {query}",
        view=Pages(
            children=[
                Page(
                    title="Results",
                    children=[
                        Grid(
                            min_column_width="300px",
                            gap=4,
                            children=[
                                Card(
                                    css_class="pf-glass",
                                    children=[
                                        CardHeader(
                                            children=[
                                                CardTitle(r["title"]),
                                                Text(
                                                    f"{r['type']} • Score: {r['score']:.2f}",
                                                    size="xs",
                                                    color="muted",
                                                ),
                                            ]
                                        ),
                                        CardContent(
                                            children=[
                                                Text(
                                                    r["content"][:150] + "...",
                                                    size="sm",
                                                    color="muted",
                                                ),
                                            ]
                                        ),
                                        CardFooter(
                                            children=[
                                                Button(
                                                    label="Read",
                                                    on_click=f"read_note:{r['permalink']}",
                                                    variant="default",
                                                )
                                            ]
                                        ),
                                    ],
                                )
                                for r in results
                            ],
                        )
                    ],
                ),
                Page(
                    title="Context Graph",
                    children=[Text("Graph view for these results coming soon...", size="lg")],
                ),
            ]
        ),
    )


def ZettelCollector() -> PrefabApp:
    """Low-friction capture UI for off-the-cuff notes."""
    return PrefabApp(
        title="Quick Zettel",
        view=Pages(
            children=[
                Page(
                    title="Capture",
                    children=[
                        Card(
                            css_class="pf-glass",
                            children=[
                                CardHeader(children=[CardTitle("Atomic Thought")]),
                                CardContent(
                                    children=[
                                        Text(
                                            "Drop your raw thought here. It will be tagged as #zettel automatically.",
                                            color="muted",
                                        ),
                                    ]
                                ),
                                CardFooter(
                                    children=[
                                        Button(
                                            label="Save as Zettel",
                                            on_click="write_note:zettel",
                                            variant="success",
                                        )
                                    ]
                                ),
                            ],
                        )
                    ],
                )
            ]
        ),
    )

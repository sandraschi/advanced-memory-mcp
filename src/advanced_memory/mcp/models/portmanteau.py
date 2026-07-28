"""
SOTA Portmanteau Schema Definitions (FastMCP 3.2+)
Uses Discriminated Unions for optimal LLM discovery and strict parameter validation.
"""

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field

# --- SHARED MODELS ---


class BaseOp(BaseModel):
    project: Annotated[str | None, Field(description="Project context override")] = None


# --- AUDIO DOMAIN ---


class AudioDictateOp(BaseOp):
    operation: Literal["dictate"]
    audio_path: Annotated[str | None, Field(description="Path to existing audio file for transcription")] = None
    record_duration: Annotated[
        int | None, Field(description="Seconds to record from default microphone if audio_path is not provided")
    ] = None
    tags: Annotated[str | list[str] | None, Field(description="Metadata tags to classify the resulting note")] = None


class AudioSpeakOp(BaseOp):
    operation: Literal["speak"]
    identifier: Annotated[str, Field(description="Note title, permalink, or raw text to read aloud")]
    voice: Annotated[str | None, Field(description="Specific Kokoro or system voice name")] = None
    speed: Annotated[float, Field(description="Playback speed multiplier (0.5 to 2.0)", ge=0.5, le=2.0)] = 1.0
    volume: Annotated[int, Field(description="Output volume level (1 to 10)", ge=1, le=10)] = 5
    save_audio: Annotated[bool, Field(description="If true, saves as WAV instead of playing locally")] = False


class AudioListenOp(BaseOp):
    operation: Literal["listen"]
    record_duration: Annotated[int, Field(description="Listening window for voice command in seconds")] = 5
    audio_path: Annotated[str | None, Field(description="Path to existing command recording for debug")] = None


class AudioWakeStartOp(BaseOp):
    operation: Literal["wake_start"]
    wake_word: Annotated[str, Field(description="Trigger word to activate background listener")] = "memorizer"
    record_duration: Annotated[int, Field(description="Seconds to record after wake word detection")] = 5


class AudioWakeStopOp(BaseModel):
    operation: Literal["wake_stop"]


class AudioWakeStatusOp(BaseModel):
    operation: Literal["wake_status"]


class AudioWeatherOp(BaseModel):
    operation: Literal["weather"]
    location: Annotated[str | None, Field(description="City or region for the weather report")] = None


class AudioTimerOp(BaseModel):
    operation: Literal["timer"]
    duration: Annotated[str, Field(description="Relative time string (e.g., '5 minutes')")]


class AudioAlarmOp(BaseModel):
    operation: Literal["alarm"]
    time_str: Annotated[str, Field(description="Absolute time string (e.g., '7:00 AM')")]


class AudioMusicOp(BaseModel):
    operation: Literal["music"]
    command: Annotated[str, Field(description="Playback command: play, pause, next, previous")]
    query: Annotated[str | None, Field(description="Search term for playback (artist, song, album)")] = None


AudioOperation = Annotated[
    AudioDictateOp
    | AudioSpeakOp
    | AudioListenOp
    | AudioWakeStartOp
    | AudioWakeStopOp
    | AudioWakeStatusOp
    | AudioWeatherOp
    | AudioTimerOp
    | AudioAlarmOp
    | AudioMusicOp,
    Field(discriminator="operation"),
]

# --- SKILLS DOMAIN ---


class SkillsCreateOp(BaseOp):
    operation: Literal["create"]
    skill_name: Annotated[str, Field(description="Unique hyphen-case identifier for the skill (e.g., 'python-expert')")]
    description: Annotated[
        str, Field(description="Clear explanation of when Claude should use this skill (no angle brackets)")
    ]
    category: Annotated[str | None, Field(description="Optional category folder (e.g., 'developer', 'research')")] = (
        None
    )
    difficulty: Annotated[str | None, Field(description="Target proficiency level")] = None
    metadata: Annotated[dict | None, Field(description="Custom metadata dictionary")] = None


class SkillsReadOp(BaseOp):
    operation: Literal["read"]
    identifier: Annotated[str, Field(description="Skill name or permalink to retrieve")]


class SkillsUpdateOp(BaseOp):
    operation: Literal["update"]
    identifier: Annotated[str, Field(description="Skill name or permalink to update")]
    content: Annotated[str, Field(description="New markdown content for the SKILL.md file")]


class SkillsDeleteOp(BaseOp):
    operation: Literal["delete"]
    identifier: Annotated[str, Field(description="Skill name or permalink to permanently remove")]


class SkillsListOp(BaseOp):
    operation: Literal["list"]
    category: Annotated[str | None, Field(description="Filter by skill category")] = None
    page: Annotated[int, Field(description="Results page number")] = 1
    page_size: Annotated[int, Field(description="Items per page")] = 20


class SkillsActivateOp(BaseOp):
    operation: Literal["activate"]
    identifier: Annotated[str, Field(description="Skill name to load into active context")]
    scope: Annotated[
        Literal["message", "session", "persistent"], Field(description="Lifespan of the skill activation")
    ] = "session"


class SkillsDeactivateOp(BaseOp):
    operation: Literal["deactivate"]
    identifier: Annotated[str | None, Field(description="Specific skill to unload")] = None
    all: Annotated[bool, Field(description="If true, clear all active skills from context")] = False


class SkillsActiveOp(BaseOp):
    operation: Literal["active"]
    verbose: Annotated[bool, Field(description="Include detailed metadata and activation times")] = False


class SkillsLoadSectionOp(BaseOp):
    operation: Literal["load_section"]
    identifier: Annotated[str, Field(description="Skill name containing the section")]
    section: Annotated[str, Field(description="Section header title (e.g., 'Decorators')")]


class SkillsLoadResourceOp(BaseOp):
    operation: Literal["load_resource"]
    identifier: Annotated[str, Field(description="Skill name containing the resource")]
    resource: Annotated[str, Field(description="Relative path to asset (e.g., 'scripts/linter.py')")]


# Distillation operations (source-specific)
class SkillsDistillWikiOp(BaseOp):
    operation: Literal["distill_from_wikipedia"]
    topic: Annotated[str, Field(description="Subject matter to investigate")]
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None
    quality: Annotated[
        Literal["basic", "comprehensive", "expert"], Field(description="Depth of the resulting distillation")
    ] = "comprehensive"


class SkillsDistillArxivOp(BaseOp):
    operation: Literal["distill_from_arxiv"]
    topic: Annotated[str, Field(description="Subject matter to investigate")]
    query: Annotated[str | None, Field(description="Specific search query (optional)")] = None
    max_papers: Annotated[int, Field(description="Number of papers to synthesize", ge=1, le=10)] = 5
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None


class SkillsDistillTextbookOp(BaseOp):
    operation: Literal["distill_from_textbook"]
    topic: Annotated[str, Field(description="Subject matter to investigate")]
    pdf_path: Annotated[str, Field(description="Path to the textbook PDF")]
    chapters: Annotated[list[int] | None, Field(description="Specific chapters to distill")] = None
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None


class SkillsDistillTextOp(BaseOp):
    operation: Literal["distill_from_text"]
    topic: Annotated[str, Field(description="Subject matter to investigate")]
    text_path: Annotated[str, Field(description="Path to the source text file")]
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None


class SkillsDistillExpertOp(BaseOp):
    operation: Literal["distill_from_expert"]
    topic: Annotated[str, Field(description="Subject matter to investigate")]
    expert_name: Annotated[str, Field(description="Name or persona of the expert source")]
    focus_area: Annotated[str | None, Field(description="Specific sub-topic to focus on")] = None
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None


class SkillsImportGithubOp(BaseOp):
    operation: Literal["import_from_github"]
    repository: Annotated[str, Field(description="GitHub repository (owner/repo)")]
    branch: Annotated[str, Field(description="Target branch")] = "main"
    category: Annotated[str | None, Field(description="Category folder for the generated skill")] = None


SkillsOperation = Annotated[
    SkillsCreateOp
    | SkillsReadOp
    | SkillsUpdateOp
    | SkillsDeleteOp
    | SkillsListOp
    | SkillsActivateOp
    | SkillsDeactivateOp
    | SkillsActiveOp
    | SkillsLoadSectionOp
    | SkillsLoadResourceOp
    | SkillsDistillWikiOp
    | SkillsDistillArxivOp
    | SkillsDistillTextbookOp
    | SkillsDistillTextOp
    | SkillsDistillExpertOp
    | SkillsImportGithubOp,
    Field(discriminator="operation"),
]

# --- INBOX DOMAIN ---


class InboxStatusOp(BaseModel):
    operation: Literal["status"]


class InboxProcessOp(BaseModel):
    operation: Literal["process"]
    file_name: Annotated[
        str | None, Field(description="Optional specific file to process (relative to inbox root)")
    ] = None


class InboxWatchOp(BaseModel):
    operation: Literal["watch"]


class InboxInfoOp(BaseModel):
    operation: Literal["info"]


InboxOperation = Annotated[
    InboxStatusOp | InboxProcessOp | InboxWatchOp | InboxInfoOp, Field(discriminator="operation")
]
# --- NOTES DOMAIN ---


class NotesWriteOp(BaseOp):
    operation: Literal["write"]
    title: Annotated[str, Field(description="Unique title for the note")]
    content: Annotated[str, Field(description="Markdown body content")]
    folder: Annotated[str, Field(description="Target vault folder")] = "inbox"
    tags: Annotated[str | list[str] | None, Field(description="Tags string or list")] = None


class NotesReadOp(BaseOp):
    operation: Literal["read"]
    identifier: Annotated[str, Field(description="Title, permalink, or memory:// URL")]
    page: Annotated[int, Field(description="Page number", ge=1)] = 1
    page_size: Annotated[int, Field(description="Items per page", ge=1, le=100)] = 20


class NotesEditOp(BaseOp):
    operation: Literal["edit"]
    identifier: Annotated[str, Field(description="Title or permalink of the note to modify")]
    mode: Annotated[
        Literal["append", "prepend", "replace_section", "find_replace"], Field(description="Mutation strategy")
    ]
    content: Annotated[str, Field(description="New content or replacement text")]
    section: Annotated[str | None, Field(description="Target section header for replace_section")] = None
    find_text: Annotated[str | None, Field(description="Text to search for in find_replace mode")] = None


class NotesDeleteOp(BaseOp):
    operation: Literal["delete"]
    identifier: Annotated[str, Field(description="Note title or permalink to remove")]


class NotesMoveOp(BaseOp):
    operation: Literal["move"]
    identifier: Annotated[str, Field(description="Note title or permalink to move")]
    destination: Annotated[str, Field(description="New folder path relative to project root")]


class NotesQuickOp(BaseOp):
    operation: Literal["quick"]
    content: Annotated[str, Field(description="Thought or content to capture")]
    tags: Annotated[str | list[str] | None, Field(description="Optional tags")] = None


class NotesDailyOp(BaseOp):
    operation: Literal["daily"]
    content: Annotated[str, Field(description="Entry content for today's log")]
    tags: Annotated[str | list[str] | None, Field(description="Optional tags")] = "daily-log"


NotesOperation = Annotated[
    NotesWriteOp | NotesReadOp | NotesEditOp | NotesDeleteOp | NotesMoveOp | NotesQuickOp | NotesDailyOp,
    Field(discriminator="operation"),
]

# --- KNOWLEDGE DOMAIN ---


class KnowledgeSuggestTagsOp(BaseOp):
    operation: Literal["suggest_tags"]
    identifier: Annotated[str, Field(description="Note title or permalink to analyze")]


class KnowledgeSummarizeOp(BaseOp):
    operation: Literal["summarize"]
    identifier: Annotated[str, Field(description="Note title or permalink to summarize")]


class KnowledgeEnhanceOp(BaseOp):
    operation: Literal["enhance"]
    identifier: Annotated[str, Field(description="Note title or permalink to improve")]
    update_style: Annotated[bool, Field(description="If true, improves tone and structure")] = True
    add_context: Annotated[bool, Field(description="If true, pulls in linked definitions")] = False
    expand: Annotated[bool, Field(description="If true, expands thin sections")] = False


class KnowledgeQCOp(BaseOp):
    operation: Literal["qc"]
    mode: Annotated[Literal["find_runts", "find_junk"], Field(description="QC strategy")]
    folder: Annotated[str | None, Field(description="Optional folder to scan")] = None
    max_length: Annotated[int, Field(description="Character limit for runt detection")] = 500


class KnowledgeCanvasOp(BaseOp):
    operation: Literal["canvas"]
    title: Annotated[str, Field(description="Title of the canvas file")]
    nodes: Annotated[list[dict], Field(description="List of node objects (file, text, link, group)")]
    edges: Annotated[list[dict], Field(description="List of edge objects (connections)")]
    folder: Annotated[str, Field(description="Target folder path relative to project root")]


class KnowledgeBulkOp(BaseOp):
    operation: Literal["bulk"]
    bulk_operation: Annotated[
        Literal[
            "tag_analytics",
            "consolidate_tags",
            "tag_maintenance",
            "bulk_update",
            "validate_content",
            "project_stats",
            "find_duplicates",
            "bulk_move",
            "bulk_delete",
        ],
        Field(description="Specific bulk operation to perform"),
    ]
    filters: Annotated[dict | None, Field(description="Search filters to select entities")] = None
    action: Annotated[dict | None, Field(description="Parameters for the bulk action")] = None
    limit: Annotated[int, Field(description="Maximum number of entities to affect")] = 0
    dry_run: Annotated[bool, Field(description="If true, only report what would change")] = True


class KnowledgeAnalyzeOp(BaseOp):
    operation: Literal["analyze"]
    analysis_type: Annotated[
        Literal["analyze_quality", "suggest_relationships", "find_gaps", "cluster_content", "extract_insights"],
        Field(description="Type of LLM analysis to perform"),
    ]
    filters: Annotated[
        dict | None, Field(description="Context filters (e.g. {'note_id': '...'} or {'topics': [...]})")
    ] = None
    action: Annotated[dict | None, Field(description="Analysis parameters")] = None
    limit: Annotated[int, Field(description="Max items to analyze")] = 10


KnowledgeOperation = Annotated[
    KnowledgeSuggestTagsOp
    | KnowledgeSummarizeOp
    | KnowledgeEnhanceOp
    | KnowledgeQCOp
    | KnowledgeCanvasOp
    | KnowledgeBulkOp
    | KnowledgeAnalyzeOp,
    Field(discriminator="operation"),
]

# --- SEARCH DOMAIN ---


class SearchQueryOp(BaseOp):
    operation: Literal["query"]
    text: Annotated[str, Field(description="Search term or boolean logic query")]
    search_type: Annotated[
        Literal["text", "title", "permalink", "tag"], Field(description="Scope of the search focus")
    ] = "text"
    page: Annotated[int, Field(description="Results page number")] = 1
    page_size: Annotated[int, Field(description="Items per page")] = 10


class SearchRagOp(BaseOp):
    operation: Literal["rag"]
    prompt: Annotated[str, Field(description="Semantic query or context prompt to ground")]
    limit: Annotated[int, Field(description="Maximum number of high-density chunks to return")] = 5
    min_score: Annotated[float, Field(description="Relevance threshold (0.0 to 1.0)")] = 0.5


class SearchExternalOp(BaseOp):
    operation: Literal["external"]
    source: Annotated[
        Literal["obsidian", "joplin", "notion", "evernote"], Field(description="External storage platform")
    ]
    path: Annotated[str, Field(description="Absolute path to the vault or export directory")]
    query: Annotated[str, Field(description="Search term")]
    max_results: Annotated[int, Field(description="Limit on returned items")] = 10


SearchOperation = Annotated[SearchQueryOp | SearchRagOp | SearchExternalOp, Field(discriminator="operation")]

# --- PROJECT DOMAIN ---


class ProjectLsOp(BaseModel):
    operation: Literal["ls"]


class ProjectCreateOp(BaseModel):
    operation: Literal["create"]
    name: Annotated[str, Field(description="Unique hyphen-case identifier for the project")]
    path: Annotated[str, Field(description="Absolute file system path to the project root directory")]
    set_default: Annotated[bool, Field(description="If true, loads this project automatically on startup")] = False


class ProjectSwitchOp(BaseModel):
    operation: Literal["switch"]
    name: Annotated[str, Field(description="Name or identifier of the project to activate")]


class ProjectRmOp(BaseModel):
    operation: Literal["rm"]
    name: Annotated[str, Field(description="Name of the project to remove from registry")]


class ProjectStatusOp(BaseModel):
    operation: Literal["status"]
    name: Annotated[str | None, Field(description="Project name (defaults to active project)")] = None


class ProjectDetectOp(BaseModel):
    operation: Literal["detect"]


ProjectOperation = Annotated[
    ProjectLsOp | ProjectCreateOp | ProjectSwitchOp | ProjectRmOp | ProjectStatusOp | ProjectDetectOp,
    Field(discriminator="operation"),
]

# --- SYSTEM DOMAIN ---


class SystemStatusOp(BaseModel):
    operation: Literal["status"]
    focus: Annotated[str | None, Field(description="Specific area of focus (e.g., 'db', 'audio', 'memory')")] = None
    level: Annotated[Literal["basic", "detailed", "expert"], Field(description="Depth of the status report")] = "basic"


class SystemHelpOp(BaseModel):
    operation: Literal["help"]
    topic: Annotated[str | None, Field(description="Specific feature or tool to get help on")] = None
    level: Annotated[
        Literal["basic", "intermediate", "expert"], Field(description="Detail level of the documentation")
    ] = "intermediate"


class SystemWorkflowOp(BaseOp):
    operation: Literal["workflow"]
    goal: Annotated[str, Field(description="Directly articulated goal for the autonomous agent to solve")]


class SystemExternalOp(BaseModel):
    operation: Literal["external_bridge"]
    server: Annotated[str, Field(description="Target MCP server name (e.g., 'speech-mcp')")]
    tool: Annotated[str, Field(description="Target tool within the external server")]
    args: Annotated[dict, Field(description="JSON parameters for the tool call")] = {}


class SystemSyncOp(BaseModel):
    operation: Literal["sync"]


SystemOperation = Annotated[
    SystemStatusOp | SystemHelpOp | SystemWorkflowOp | SystemExternalOp | SystemSyncOp, Field(discriminator="operation")
]

# --- TYPORA DOMAIN ---


class TyporaOpenOp(BaseModel):
    operation: Literal["open"]
    file_path: Annotated[str, Field(description="Absolute path to the markdown file to open in Typora")]


class TyporaSaveOp(BaseModel):
    operation: Literal["save"]


class TyporaInsertOp(BaseModel):
    operation: Literal["insert"]
    text: Annotated[str, Field(description="Text or markdown to insert")]
    position: Annotated[str | None, Field(description="Target location anchor or 'current cursor'")] = "current cursor"


class TyporaGetContentOp(BaseModel):
    operation: Literal["get_content"]


class TyporaSetContentOp(BaseModel):
    operation: Literal["set_content"]
    content: Annotated[str, Field(description="New markdown body to replace the current document")]


class TyporaCursorOp(BaseModel):
    operation: Literal["cursor"]


class TyporaAnalyzeOp(BaseModel):
    operation: Literal["analyze"]


class TyporaExportOp(BaseModel):
    operation: Literal["export"]
    format: Annotated[Literal["pdf", "html", "docx", "odt"], Field(description="Target export format")]
    path: Annotated[str, Field(description="Absolute destination path for the exported file")]
    options: Annotated[dict | None, Field(description="Format-specific export parameters")] = None


TyporaOperation = Annotated[
    TyporaOpenOp
    | TyporaSaveOp
    | TyporaInsertOp
    | TyporaGetContentOp
    | TyporaSetContentOp
    | TyporaCursorOp
    | TyporaAnalyzeOp
    | TyporaExportOp,
    Field(discriminator="operation"),
]

# --- ZETTEL DOMAIN ---


class ZettelGenerateOp(BaseOp):
    operation: Literal["generate"]
    topic: Annotated[str, Field(description="Specific topic or keyword for the new note")]
    category: Annotated[str, Field(description="Taxonomy category (e.g., developer, business, math, science)")]
    quality: Annotated[
        Literal["quick", "standard", "comprehensive", "expert"], Field(description="Level of detail and rigor")
    ] = "standard"
    ai_generate: Annotated[bool, Field(description="If true, uses LLM to bridge gaps in local templates")] = True


class ZettelExpandOp(BaseOp):
    operation: Literal["expand"]
    note_identifier: Annotated[str, Field(description="Title or permalink of the existing note to develop")]
    depth: Annotated[int, Field(description="Iteration depth for horizontal expansion (1-5)", ge=1, le=5)] = 1


class ZettelSuggestOp(BaseOp):
    operation: Literal["suggest"]
    category: Annotated[str | None, Field(description="Focus recommendations on a specific domain")] = None
    count: Annotated[int, Field(description="Number of intelligent topics to propose")] = 5


class ZettelConnectOp(BaseOp):
    operation: Literal["connect"]
    note_identifier: Annotated[str | None, Field(description="Optional anchor note for relationship discovery")] = None


class ZettelAnalyzeOp(BaseOp):
    operation: Literal["analyze"]
    category: Annotated[str | None, Field(description="Scope analysis to a specific taxonomy folder")] = None


class ZettelCustomizeOp(BaseOp):
    operation: Literal["customize"]
    category: Annotated[str, Field(description="Template category (e.g., 'developer', 'researcher')")]
    topic: Annotated[str, Field(description="Specific topic name within the category")]
    depth: Annotated[int, Field(description="Generation depth level (1-5)")] = 3


class ZettelCollectOp(BaseModel):
    operation: Literal["collect"]


ZettelOperation = Annotated[
    ZettelGenerateOp
    | ZettelExpandOp
    | ZettelSuggestOp
    | ZettelConnectOp
    | ZettelAnalyzeOp
    | ZettelCustomizeOp
    | ZettelCollectOp,
    Field(discriminator="operation"),
]

# --- NAV DOMAIN ---


class NavLsOp(BaseOp):
    operation: Literal["ls"]
    path: Annotated[str | None, Field(description="Relative folder path to list (defaults to project root)")] = "/"


class NavRecentOp(BaseOp):
    operation: Literal["recent"]
    timeframe: Annotated[str, Field(description="Lookback window (e.g. 'yesterday', 'today', '7d')")] = "7d"
    page: Annotated[int, Field(description="Results page number")] = 1
    page_size: Annotated[int, Field(description="Items per page")] = 20


class NavSyncOp(BaseOp):
    operation: Literal["sync"]


class NavStatusOp(BaseOp):
    operation: Literal["status"]


class NavBacklinksOp(BaseOp):
    operation: Literal["backlinks"]
    identifier: Annotated[str, Field(description="Title or permalink of the target note")]


class NavBuildContextOp(BaseOp):
    operation: Literal["build_context"]
    url: Annotated[str, Field(description="Memory URI (memory://project/permalink) to explore")]
    depth: Annotated[int, Field(description="Relation traversal depth (1-3)", ge=1, le=3)] = 1
    max_related: Annotated[int, Field(description="Limit of related notes per level")] = 10


NavOperation = Annotated[
    NavLsOp | NavRecentOp | NavSyncOp | NavStatusOp | NavBacklinksOp | NavBuildContextOp,
    Field(discriminator="operation"),
]

# --- AUTOMATION DOMAIN ---


class AutomationWorkflowOp(BaseOp):
    operation: Literal["workflow"]
    goal: Annotated[str, Field(description="The high-level objective or processing prompt for the autonomous agent")]
    tools: Annotated[list[str] | None, Field(description="Subset of tools allowed for the autonomous agent")] = None
    iterations: Annotated[int, Field(description="Maximum steps for a workflow", ge=1, le=50)] = 5


class AutomationBatchOp(BaseOp):
    operation: Literal["batch"]
    goal: Annotated[str, Field(description="The processing prompt to apply to each item in the batch")]
    items: Annotated[list[str], Field(description="List of note identifiers or memory:// URLs to process")]
    tools: Annotated[list[str] | None, Field(description="Subset of tools allowed for the batch processor")] = None


class AutomationStatusOp(BaseModel):
    operation: Literal["status"]


AutomationOperation = Annotated[
    AutomationWorkflowOp | AutomationBatchOp | AutomationStatusOp, Field(discriminator="operation")
]

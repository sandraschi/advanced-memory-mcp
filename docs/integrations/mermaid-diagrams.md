# Mermaid Diagrams in Basic Memory

Basic Memory now supports Mermaid diagrams, allowing you to create and view various types of diagrams directly in your notes. This guide explains how to use Mermaid diagrams effectively within the Basic Memory ecosystem.

## Overview

[Mermaid](https://mermaid.js.org/) is a JavaScript-based diagramming tool that renders Markdown-inspired text definitions to create diagrams. It's perfectly suited for Basic Memory because:

- **Text-based**: Diagrams are stored as plain text in your notes
- **Version controllable**: Full git history of diagram changes
- **Portable**: Works across all platforms without special software
- **Integrated**: Renders automatically in HTML exports

## Quick Start

### Basic Flowchart

Add this to any note:

````markdown
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
    D --> F[End]
    E --> F
```
````

### Export to HTML

Use the HTML export tool to see your diagrams rendered:

```bash
# Export notes with Mermaid diagrams
await export_html_notes.fn(export_path="/path/to/html-export")
```

The exported HTML files will automatically render all Mermaid diagrams.

## Supported Diagram Types

### 1. Flowcharts

Perfect for process documentation, decision trees, and workflows.

```mermaid
graph TD
    A[User Login] --> B[Validate Credentials]
    B --> C[Credentials Valid?]
    C -->|Yes| D[Grant Access]
    C -->|No| E[Show Error]
    D --> F[Dashboard]
    E --> A
```

### 2. Sequence Diagrams

Great for API interactions, user workflows, and system communications.

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as Database

    U->>A: Login Request
    A->>D: Validate User
    D-->>A: User Data
    A-->>U: JWT Token
    U->>A: Protected Request
    A-->>U: Response
```

### 3. Gantt Charts

Ideal for project timelines and task dependencies.

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Requirements      :done, req, 2024-01-01, 2024-01-15
    Design            :done, des, after req, 2024-01-10
    section Development
    Implementation    :active, impl, after des, 2024-02-01
    Testing           :test, after impl, 2024-02-15
    section Deployment
    Launch            :milestone, launch, after test, 2024-03-01
```

### 4. Mind Maps

Excellent for brainstorming, knowledge organization, and concept mapping.

```mermaid
mindmap
  root((Basic Memory))
    Features
      Markdown Notes
      Version Control
      Search
      Export Tools
    Integrations
      Typora Editing
      HTML Export
      Mermaid Diagrams
      Obsidian Import
    Use Cases
      Personal Knowledge
      Project Documentation
      Research Notes
      Task Management
```

### 5. Entity Relationship Diagrams

Useful for data modeling and system architecture.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {{
        string name
        string custNumber
        string sector
    }}
    ORDER {{
        int orderNumber
        string deliveryAddress
    }}
    LINE-ITEM {{
        string productCode
        int quantity
        float pricePerUnit
    }}
```

### 6. State Diagrams

Good for representing system states, user journeys, and process flows.

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

### 7. Pie Charts

Simple data visualization within notes.

```mermaid
pie title Project Distribution
    "Feature Development" : 45
    "Bug Fixes" : 25
    "Documentation" : 15
    "Testing" : 10
    "Planning" : 5
```

## Diagram Templates

### Project Planning Template

````markdown
# Project Alpha Planning

## Project Overview
[Project description here]

## Workflow Diagram
```mermaid
graph TD
    A[Project Start] --> B[Requirements]
    B --> C[Design]
    C --> D[Development]
    D --> E[Testing]
    E --> F[Deployment]
    F --> G[Maintenance]

    C --> H[Design Review]
    H --> D

    D --> I[Code Review]
    I --> E
```
````

### Knowledge Map Template

````markdown
# Knowledge Domain Map

## Overview
[Description of the knowledge domain]

## Concept Relationships
```mermaid
mindmap
  root((Machine Learning))
    Supervised Learning
      Classification
      Regression
    Unsupervised Learning
      Clustering
      Dimensionality Reduction
    Deep Learning
      Neural Networks
      CNN
      RNN
    Applications
      Computer Vision
      NLP
      Recommendation Systems
```
````

### API Documentation Template

````markdown
# User Authentication API

## Authentication Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth Service
    participant D as Database
    participant R as Resource Server

    C->>A: POST /login
    A->>D: Validate credentials
    D-->>A: User data
    A->>A: Generate JWT
    A-->>C: JWT token

    C->>R: GET /protected (with JWT)
    R->>R: Validate JWT
    R-->>C: Protected data
```
````

## Best Practices

### 1. Keep Diagrams Simple
- Focus on clarity over complexity
- Use descriptive labels
- Avoid overly dense diagrams

### 2. Use Consistent Naming
- Use consistent terminology across diagrams
- Follow naming conventions
- Include units where relevant

### 3. Version Control Friendly
- Store diagrams in dedicated notes
- Use meaningful filenames
- Include diagram descriptions

### 4. Accessibility
- Use high contrast colors when possible
- Include text descriptions
- Ensure diagrams make sense when read aloud

## Integration with Typora

Since Basic Memory integrates with Typora, you can:

1. **Edit diagrams visually** in Typora's live preview
2. **Use Typora's themes** for consistent styling
3. **Export diagrams** to various formats through Typora
4. **Get real-time feedback** on diagram syntax

### Typora Workflow

1. Export note to Typora using `edit_in_typora`
2. Edit diagram in Typora's live preview
3. Save changes and import back with `import_from_typora`
4. Export to HTML to see final rendered result

## Troubleshooting

### Diagrams Not Rendering

**HTML Export Issues:**
- Ensure you're using the latest HTML export tool
- Check browser console for JavaScript errors
- Verify internet connection for CDN resources

**Syntax Errors:**
- Use online Mermaid editor to validate syntax
- Check for missing semicolons or brackets
- Ensure proper indentation

### Performance Issues

**Large Diagrams:**
- Break complex diagrams into smaller ones
- Use subgraphs to organize content
- Consider using external diagram tools for very large diagrams

**Loading Issues:**
- Diagrams load asynchronously - wait for page to fully load
- Check network connectivity for CDN resources
- Try refreshing the page

## Advanced Usage

### Custom Styling

You can customize diagram appearance using Mermaid's configuration:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#ff0000' }}}%%
graph TD
    A[Styled Node] --> B[Another Node]
```

### Interactive Diagrams

Some diagram types support interactivity:

```mermaid
graph TD
    A[Click me] --> B[Hidden]
    click A "https://example.com" "Open link"
```

### Integration with Note Links

Combine Mermaid with Basic Memory's linking:

```mermaid
graph TD
    A[Project Overview] --> B[Requirements]
    A --> C[Architecture]
    B --> D[Detailed Specs]

    click B "requirements.md" "View requirements"
    click C "architecture.md" "View architecture"
    click D "specs.md" "View specifications"
```

## Examples Gallery

### Decision Tree
```mermaid
graph TD
    A[Need to make decision?] -->|Yes| B[Define criteria]
    A -->|No| C[No action needed]
    B --> D[Gather information]
    D --> E[Evaluate options]
    E --> F[Make choice]
    F --> G[Implement decision]
    G --> H[Monitor results]
```

### User Journey
```mermaid
journey
    title User Registration Journey
    section Discovery
        Research: 3: User
        Compare options: 4: User
    section Signup
        Visit website: 5: User
        Create account: 3: User
        Verify email: 2: User
    section Onboarding
        Complete profile: 4: User
        First login: 5: User
        Explore features: 4: User
```

### Git Flow
```mermaid
gitgraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add feature structure"
    branch feature/login
    checkout feature/login
    commit id: "Implement login form"
    commit id: "Add validation"
    checkout develop
    merge feature/login
    checkout main
    merge develop
    release id: "v1.0.0"
```

## Resources

- [Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [Typora Mermaid Support](https://support.typora.io/Mermaid/)
- [Mermaid Configuration](https://mermaid.js.org/config/)

## Contributing

Found useful diagram templates or have improvements? Consider:

1. Adding templates to the Basic Memory documentation
2. Sharing diagram patterns with the community
3. Contributing to Mermaid's development

---

*Last updated: [Current Date]*
*Basic Memory Version: 0.14.x*

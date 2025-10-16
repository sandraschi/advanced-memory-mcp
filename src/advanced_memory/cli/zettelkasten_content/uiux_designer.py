"""UI/UX Designer Zettelkasten Templates - Design principles, tools, and user experience notes."""

UIUX_DESIGNER_TEMPLATES = {
    "design-principles": [
        {
            "title": "Design Principles Fundamentals",
            "folder": "design/principles",
            "content": r"""# Design Principles Fundamentals

Core design principles that guide effective user interface and experience design.

## The Gestalt Principles

### 1. Proximity
Elements close together are perceived as related.

- [principle] Group related items together
- [application] Use white space to separate unrelated sections
- [benefit] Reduces cognitive load

### 2. Similarity
Similar elements are perceived as belonging together.

- [principle] Use consistent styling for related elements
- [application] Buttons with same function should look the same
- [benefit] Creates visual hierarchy

### 3. Continuity
Eyes follow lines and curves naturally.

- [principle] Align elements along visual paths
- [application] Use grids and alignment guides
- [benefit] Smooth visual flow

### 4. Closure
Mind fills in missing information.

- [principle] Don't over-explain with visuals
- [application] Logos can be simplified
- [benefit] Cleaner, more memorable designs

## Visual Hierarchy

```
Primary (Largest, boldest)
  └─ Secondary (Medium weight)
      └─ Tertiary (Smallest, lightest)
```

- [definition] Visual Hierarchy: Arrangement of elements by importance
- [technique] Size, color, contrast, position, whitespace
- [goal] Guide user's attention to most important information

## Typography Principles

### Font Selection
- **Serif**: Traditional, readable for long text (Times, Georgia)
- **Sans-serif**: Modern, clean for screens (Helvetica, Roboto)
- **Display**: Decorative, use sparingly for headings

```css
/* Typography scale */
h1 { font-size: 2.5rem; }    /* 40px */
h2 { font-size: 2rem; }      /* 32px */
h3 { font-size: 1.5rem; }    /* 24px */
body { font-size: 1rem; }    /* 16px */
small { font-size: 0.875rem; } /* 14px */
```

- [rule] Limit to 2-3 fonts maximum
- [rule] Line height 1.4-1.6 for readability
- [rule] Line length 50-75 characters optimal

## Color Theory

### Color Wheel Relationships
- **Complementary**: Opposite on wheel (high contrast)
- **Analogous**: Adjacent on wheel (harmonious)
- **Triadic**: Three evenly spaced colors (balanced)

### 60-30-10 Rule
- **60%**: Dominant color (backgrounds)
- **30%**: Secondary color (content areas)
- **10%**: Accent color (CTAs, highlights)

```css
:root {
  --primary: #2563eb;    /* 60% - Blue */
  --secondary: #64748b;  /* 30% - Slate */
  --accent: #f59e0b;     /* 10% - Amber */
}
```

- [principle] Use color purposefully, not decoratively
- [accessibility] Ensure sufficient contrast (WCAG AA: 4.5:1)

## White Space (Negative Space)

- [definition] Empty space around and between elements
- [purpose] Improves readability and focus
- [mistake] Cramming too much without breathing room

## Relations
- enables [[UI Design Best Practices]]
- related_to [[Accessibility Design]]
- uses [[Color Theory]]
- builds_on [[Visual Hierarchy]]

## Practical Application

1. **Start with hierarchy**: What's most important?
2. **Apply proximity**: Group related elements
3. **Use whitespace**: Let design breathe
4. **Establish rhythm**: Consistent spacing and sizing
5. **Test with users**: Validate assumptions

*Good design is invisible - users shouldn't notice the design, only accomplish their goals.*
""",
        },
        {
            "title": "User Research Methods",
            "folder": "design/research",
            "content": r"""# User Research Methods

User research helps understand user needs, behaviors, and motivations through observation and feedback.

## Types of Research

### Qualitative Research
Understanding the "why" behind behaviors.

**Methods:**
1. **User Interviews**: One-on-one conversations
2. **Focus Groups**: Group discussions
3. **Usability Testing**: Observe users completing tasks
4. **Field Studies**: Observe in natural environment

- [goal] Understand motivations, frustrations, mental models
- [output] Insights, quotes, behavioral patterns

### Quantitative Research
Measuring and counting behaviors.

**Methods:**
1. **Surveys**: Structured questionnaires
2. **Analytics**: User behavior metrics
3. **A/B Testing**: Compare design variants
4. **Card Sorting**: Information architecture validation

- [goal] Measure trends, validate assumptions with data
- [output] Numbers, statistics, conversion rates

## User Interview Guide

### Before Interview
```markdown
**Goals:**
- Understand user's workflow
- Identify pain points
- Discover unmet needs

**Participants:**
- 5-8 users from target audience
- Mix of experience levels
- Diverse backgrounds

**Questions Prepared:**
- Open-ended ("Tell me about...")
- Avoid leading questions
- Follow-up probes ready
```

### During Interview
- **Listen more than talk** (80/20 rule)
- **Ask "why" five times** to get to root cause
- **Note exact quotes** for insights
- **Observe body language** and tone

### After Interview
- Transcribe within 24 hours
- Identify themes and patterns
- Create affinity diagrams
- Share insights with team

## Usability Testing Protocol

```mermaid
graph TB
    A[Define Tasks] --> B[Recruit Users]
    B --> C[Prepare Prototype]
    C --> D[Conduct Test]
    D --> E[Observe & Record]
    E --> F[Analyze Results]
    F --> G[Report Findings]
    G --> H[Iterate Design]
```

### Task Design
```markdown
**Task 1:** Find and purchase a blue t-shirt in size medium
- Success criteria: User completes checkout
- Time limit: 5 minutes
- Difficulty: Easy

**Metrics to Track:**
- Task success rate
- Time to completion
- Number of errors
- User satisfaction (1-5)
```

### Think-Aloud Protocol
- Ask users to verbalize their thoughts
- Don't interrupt or guide
- Note confusion points
- Record exact quotes

## User Personas

```markdown
**Sarah - The Busy Professional**

**Demographics:**
- Age: 32
- Occupation: Marketing Manager
- Tech savviness: Medium

**Goals:**
- Quickly find reliable information
- Accomplish tasks efficiently
- Minimize time spent learning new tools

**Pain Points:**
- Overwhelmed by complex interfaces
- Frustrated by slow loading times
- Needs mobile-friendly experiences

**Quote:** "I don't have time to figure out complicated systems."
```

- [tool] Personas represent user archetypes
- [benefit] Keep user needs front of mind
- [warning] Based on research, not assumptions

## Journey Mapping

```
Awareness → Consideration → Decision → Purchase → Post-Purchase

Example: Online Shopping Journey
1. See ad on social media (Awareness)
2. Visit website, browse products (Consideration)
3. Read reviews, compare prices (Decision)
4. Add to cart, checkout (Purchase)
5. Track delivery, leave review (Post-Purchase)

Touchpoints: Ads, Website, Email, Support
Emotions: 😊 → 🤔 → 😟 → 😃 → 😊
Pain Points: Slow site, unclear sizing, shipping cost surprise
```

- [tool] Journey map visualizes user experience over time
- [reveals] Emotional highs and lows
- [identifies] Optimization opportunities

## Research Planning

### When to Use What

| Method | Best For | Time Required | Users Needed |
|--------|----------|---------------|--------------|
| Interviews | Deep insights | 1-2 hours each | 5-8 |
| Surveys | Quantitative validation | 10-15 mins | 100+ |
| Usability Testing | Interface validation | 30-60 mins | 5-8 |
| Analytics | Behavior patterns | Ongoing | All users |
| A/B Testing | Design decisions | 1-2 weeks | 1000+ |

## Relations
- informs [[Design Decisions]]
- creates [[User Personas]]
- enables [[User-Centered Design]]
- related_to [[Usability Testing]]
- builds_on [[Research Methods]]

## Best Practices

1. **Start with qualitative** to understand, then quantitative to validate
2. **Recruit diverse users** to avoid bias
3. **Test early and often** throughout design process
4. **Involve stakeholders** in research observations
5. **Document everything** for future reference
6. **Act on findings** - research without action is waste

*Design without research is just guessing - validate your assumptions with real users.*
""",
        },
    ],
    "design-tools": [
        {
            "title": "Figma Essentials",
            "folder": "design/tools",
            "content": r"""# Figma Essentials

Figma is a collaborative web-based design tool for UI/UX design, prototyping, and design systems.

## Why Figma?

- [benefit] **Cloud-based**: No software installation required
- [benefit] **Real-time collaboration**: Multiple designers work simultaneously
- [benefit] **Cross-platform**: Works on Mac, Windows, Linux, Web
- [benefit] **Version history**: Automatic saving and version control
- [feature] **Components and variants**: Reusable design elements

## Core Concepts

### Frames
Container for designs (like artboards in other tools).

```
Frame (iPhone 14 Pro - 393x852px)
  ├─ Header Frame
  ├─ Content Frame
  └─ Footer Frame
```

- [concept] Frames define viewport boundaries
- [use] Create responsive designs with auto-layout

### Components
Reusable design elements.

```
Component: Button
  Variants:
    ├─ Primary (filled, blue)
    ├─ Secondary (outline, gray)
    └─ Danger (filled, red)

  States:
    ├─ Default
    ├─ Hover
    ├─ Active
    └─ Disabled
```

- [definition] Component: Master element that can be instantiated
- [benefit] Change once, updates everywhere
- [feature] Variants for different states/styles

### Auto Layout
Responsive design system that automatically adjusts to content.

```
Auto Layout Container
  Direction: Horizontal
  Padding: 16px
  Gap: 8px

  [Icon] [Text] [Badge]
```

- [feature] Elements resize based on content
- [benefit] Maintains consistent spacing
- [use-case] Responsive buttons, cards, navigation

## Design Systems in Figma

### Color Styles
```
Brand Colors:
  Primary/500: #2563eb
  Primary/600: #1d4ed8
  Primary/700: #1e40af

Semantic Colors:
  Success: #10b981
  Warning: #f59e0b
  Error: #ef4444
```

### Text Styles
```
Heading 1: Inter, 32px, Bold, 40px line height
Heading 2: Inter, 24px, SemiBold, 32px line height
Body: Inter, 16px, Regular, 24px line height
Caption: Inter, 14px, Regular, 20px line height
```

### Component Library
- Buttons (all variants and states)
- Form inputs (text, select, checkbox, radio)
- Cards and containers
- Navigation components
- Icons and illustrations

## Prototyping

### Creating Interactions
```
Frame: Login Screen
  Button: "Sign In"
    → On Click
    → Navigate to: Dashboard
    → Animation: Smart Animate
    → Easing: Ease Out
    → Duration: 300ms
```

**Interaction Types:**
- Click/Tap
- Drag
- Hover
- Key press
- After delay

**Animations:**
- Instant
- Dissolve
- Smart Animate (morphing)
- Move In/Out
- Custom easing

### Prototyping Best Practices
- Start with low-fidelity (wireframes)
- Add interactivity incrementally
- Test early with users
- Create multiple user flows
- Include error states and edge cases

## Collaboration Features

### Comments
```
Comment Thread:
  Designer: "Should this button be larger?"
  Developer: "Yes, following design system"
  Product: "Approved, matches specs"
```

### Sharing
- **View-only link**: Stakeholder review
- **Edit link**: Collaborator access
- **Dev mode**: Inspect styles and export assets
- **Present mode**: Full-screen prototype presentation

## Developer Handoff

### Inspect Panel
```
Button Component
  Size: 120 × 40px
  Border radius: 8px
  Background: #2563eb
  Padding: 12px 24px
  Font: Inter, 16px, Medium

CSS:
  width: 120px;
  height: 40px;
  background: #2563eb;
  border-radius: 8px;
  padding: 12px 24px;
```

- [feature] Auto-generated CSS/iOS/Android code
- [feature] Export assets in multiple formats
- [feature] Measure distances and spacing

## Keyboard Shortcuts

```
V - Move tool
F - Frame tool
R - Rectangle
T - Text
Cmd/Ctrl + D - Duplicate
Cmd/Ctrl + G - Group
Cmd/Ctrl + Shift + K - Place image
Cmd/Ctrl + / - Search
```

## Relations
- enables [[UI Design]]
- enables [[Design Systems]]
- enables [[Prototyping]]
- related_to [[Design Principles Fundamentals]]
- used_with [[User Research Methods]]

## Best Practices

1. **Organize with pages and frames**
2. **Use components for everything reusable**
3. **Create variants instead of duplicating components**
4. **Document with comments and descriptions**
5. **Use plugins wisely** (don't overdo it)
6. **Regular cleanupof unused elements**

*Figma's collaborative features make it the modern standard for UI design teams.*
""",
        },
    ],
}

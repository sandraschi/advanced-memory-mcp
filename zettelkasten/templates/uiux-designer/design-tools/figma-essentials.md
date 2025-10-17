# Figma Essentials

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

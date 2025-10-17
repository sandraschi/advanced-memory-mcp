# Design Principles Fundamentals

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

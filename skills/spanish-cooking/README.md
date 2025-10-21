# Spanish Cooking Expert Skill

A comprehensive Claude skill for Spanish cuisine expertise, covering traditional recipes, regional variations, and authentic cooking techniques.

## What This Skill Does

Provides expert guidance on:
- **Traditional Spanish recipes** (paella, tapas, gazpacho, tortilla)
- **Regional cuisines** (Valencia, Andalusia, Basque Country, Galicia, etc.)
- **Essential techniques** (sofrito, socarrat, alioli, octopus preparation)
- **Ingredient selection** (olive oil, saffron, pimentón, jamón)
- **Wine pairings** (Rioja, Albariño, Cava, Sherry)
- **Menu planning** (tapas nights, paella parties)

## How to Use

### In Claude Desktop

1. Copy this folder to: `~/.config/claude-desktop/skills/spanish-cooking/`
2. Claude will automatically load the skill
3. Ask questions like:
   - "How do I make authentic paella?"
   - "What are the best Spanish tapas for beginners?"
   - "Explain the difference between Jamón Serrano and Ibérico"
   - "Plan a tapas party menu for 8 people"

### Example Conversations

**Beginner:**
```
User: "I want to try making Spanish food. Where should I start?"
Claude: [Uses spanish-cooking skill]
"Great choice! For beginners, I recommend starting with three classic dishes:

1. Pan con Tomate (Catalan Tomato Bread)
2. Tortilla Española (Spanish Potato Omelet)  
3. Gambas al Ajillo (Garlic Shrimp)

Let me walk you through the tortilla española..."
```

**Intermediate:**
```
User: "I want to make paella for 6 people but I don't have bomba rice"
Claude: [Uses spanish-cooking skill]
"While bomba rice is ideal, you have options:

Best substitute: Calasparra rice (another Spanish short-grain)
Acceptable: Arborio rice (but be careful - it's starchier)

Here's how to adjust your technique with Arborio..."
```

**Advanced:**
```
User: "Explain the traditional Valencian paella vs paella mixta controversy"
Claude: [Uses spanish-cooking skill]
"Ah, this is a passionate topic in Valencia!

Traditional Paella Valenciana contains:
- Chicken, rabbit (never seafood!)
- Green beans (flat variety)
- Garrafó beans (large white beans)
- Tomato, saffron, olive oil
- Bomba rice

Paella mixta (mixed paella) adds seafood and is what most tourists eat.
Valencians consider this a different dish entirely..."
```

## Features

- ✅ Comprehensive regional knowledge
- ✅ Step-by-step technique guidance
- ✅ Ingredient substitution suggestions
- ✅ Wine and beverage pairings
- ✅ Common mistake prevention
- ✅ Cultural context and traditions
- ✅ Menu planning assistance
- ✅ Skill level adaptation

## Knowledge Source

This skill is generated from the Advanced Memory knowledge base note:
`knowledge/cooking/Spanish_Cooking_Masterclass.md`

To update this skill with new recipes or techniques:
1. Edit the source note in Advanced Memory
2. Regenerate skill: `adn_skills("from_zettel", note_identifier="Spanish Cooking Masterclass")`
3. Export to Claude Desktop

## Version History

- **1.0.0** (2025-10-21) - Initial release
  - Regional cuisines covered
  - Essential techniques documented
  - Classic recipes included
  - Wine pairing guidance

---

**Category:** Culinary  
**Difficulty:** Intermediate  
**License:** MIT

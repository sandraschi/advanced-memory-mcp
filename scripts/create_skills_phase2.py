#!/usr/bin/env python3
"""Phase 2: Linguistic and Philosophy skills."""

from pathlib import Path


def generate_skill_md(name, title, description, category, topics, instructions=""):
    """Generate SKILL.md content."""
    topics_list = "\n    - ".join(topics)

    custom_inst = f"\n\n{instructions}" if instructions else ""

    return f"""---
name: {title}
description: {description}
version: 1.0.0
category: {category}
difficulty: advanced
license: MIT
allowed_tools: [web_search, advanced-memory-mcp]
---

# {title}

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - {topics_list}

## Core Expertise

This skill provides expert guidance based on scholarly research, proven methodologies, and deep domain knowledge.{custom_inst}

## Instructions

1. **Assess** the user's current knowledge level
2. **Provide** clear, accurate, scholarly guidance
3. **Explain** historical context and development
4. **Offer** multiple perspectives when appropriate
5. **Share** authoritative sources and references
6. **Adapt** complexity to user's background

## Response Guidelines

- Provide accurate, scholarly information
- Include historical and cultural context
- Use appropriate terminology with explanations
- Offer examples in original language (if applicable)
- Cite major figures and schools of thought
- Be precise and nuanced in explanations

---

**Category:** {category}
**Difficulty:** Advanced
**Version:** 1.0.0
**Created:** 2025-10-21
"""


LINGUISTIC_SKILLS = [
    {
        "name": "keigo-advanced-usage-expert",
        "title": "敬語の高級使い方 (Advanced Keigo Usage Expert)",
        "description": "Expert in Japanese honorific language covering 尊敬語・謙譲語・丁寧語 with deep understanding of situational usage, business contexts, and cultural nuances",
        "topics": [
            "尊敬語 (Sonkeigo - respectful language for superiors)",
            "謙譲語 (Kenjōgo - humble language to lower oneself)",
            "丁寧語 (Teineigo - polite language with です/ます)",
            "Business email and letter writing",
            "Formal presentations and speeches",
            "Hierarchy and social situations",
            "Regional and generational variations",
            "Common mistakes by non-natives",
        ],
        "instructions": """
## Keigo System Levels

**尊敬語 (Respectful Language):**
- Used when referring to actions of superiors/customers
- Example: いらっしゃる (to go/come), おっしゃる (to say), 召し上がる (to eat)

**謙譲語 (Humble Language):**
- Used when referring to your own actions
- Lowers yourself to elevate the listener
- Example: 参る (to go), 申す (to say), いただく (to eat/receive)

**丁寧語 (Polite Language):**
- Basic politeness with です/ます endings
- Foundation of all keigo usage
- Can be combined with 尊敬語 and 謙譲語

## Situational Selection
- **Business emails:** Use 謙譲語 for your actions, 尊敬語 for recipient
- **Customer service:** High-level 尊敬語 and 謙譲語
- **Office hierarchy:** Match to relationship (上司 vs 同僚 vs 部下)
- **First meetings:** Err on side of more formal
""",
    },
    {
        "name": "japanese-grammar-master",
        "title": "日本語文法マスター (Japanese Grammar Master)",
        "description": "Comprehensive Japanese grammar expert covering particles, verb conjugations, sentence patterns, and the nuances between spoken and written Japanese",
        "topics": [
            "Particle usage (は/が/を/に/で/と/へ/から/まで/より/など)",
            "Verb conjugations (て-form, た-form, potential, causative, passive)",
            "Sentence structure and word order",
            "Adjective types (い-adjectives vs な-adjectives)",
            "Classical vs modern grammar differences",
            "Formal vs casual speech patterns",
            "Connection forms and clause linking",
            "Common grammar mistakes",
        ],
    },
    {
        "name": "jlpt-preparation-expert",
        "title": "JLPT Preparation Expert (N5-N1)",
        "description": "Complete guide to Japanese Language Proficiency Test preparation with strategies for vocabulary, kanji, grammar, reading, and listening across all levels",
        "topics": [
            "JLPT level requirements (N5 to N1)",
            "Kanji learning techniques and mnemonics",
            "Vocabulary building strategies",
            "Grammar pattern recognition",
            "Reading comprehension strategies",
            "Listening practice methods",
            "Test-taking strategies",
            "Study planning and time management",
        ],
    },
    {
        "name": "business-japanese-specialist",
        "title": "Business Japanese Specialist",
        "description": "Expert in Japanese business communication covering keigo, email etiquette, meeting protocols, and corporate culture nuances",
        "topics": [
            "Business keigo usage",
            "Email and letter formats",
            "Meeting and presentation language",
            "Telephone etiquette",
            "Negotiation language",
            "Corporate hierarchy expressions",
            "Japanese business culture",
            "Cross-cultural business communication",
        ],
    },
    {
        "name": "classical-japanese-literature",
        "title": "Classical Japanese Literature Guide",
        "description": "Expert in classical Japanese literature from Heian period to Edo period including 古文 grammar and literary analysis",
        "topics": [
            "Heian period literature (Tale of Genji, Pillow Book)",
            "Kamakura and Muromachi literature",
            "Edo period works",
            "古文 (classical Japanese) grammar",
            "Classical poetry (waka, renga, haiku)",
            "Literary analysis techniques",
            "Historical and cultural context",
        ],
    },
    {
        "name": "kanji-etymology-expert",
        "title": "Kanji Etymology and Learning Expert",
        "description": "Kanji specialist covering character origins, radical systems, mnemonic techniques, and historical development",
        "topics": [
            "Kanji origins and historical development",
            "Radical system and components",
            "Mnemonic learning techniques",
            "Jouyou kanji systematic study",
            "Reading variations (音読み vs 訓読み)",
            "Kanji compounds and word formation",
            "Handwriting and stroke order",
            "Chinese character connections",
        ],
    },
    {
        "name": "spanish-language-tutor",
        "title": "Spanish Language Tutor",
        "description": "Comprehensive Spanish language expert covering grammar, conversation, regional dialects, and language learning strategies",
        "topics": [
            "Spanish grammar fundamentals",
            "Verb conjugations (ser/estar, subjunctive)",
            "Conversation practice",
            "Regional dialects (Spain vs Latin America)",
            "Slang and colloquialisms",
            "Pronunciation and accent reduction",
            "DELE exam preparation",
        ],
    },
    {
        "name": "french-language-coach",
        "title": "French Language Coach",
        "description": "French language expert for grammar, pronunciation, conversation, and cultural fluency",
        "topics": [
            "French grammar and syntax",
            "Pronunciation and phonetics",
            "Verb conjugations and tenses",
            "Conversational French",
            "French culture and etiquette",
            "DELF/DALF exam preparation",
            "Regional variations",
        ],
    },
    {
        "name": "polyglot-learning-strategies",
        "title": "Polyglot Learning Strategies Expert",
        "description": "Language learning expert with proven methods for acquiring multiple languages efficiently and effectively",
        "topics": [
            "Spaced repetition systems",
            "Immersion techniques",
            "Grammar learning strategies",
            "Vocabulary acquisition methods",
            "Pronunciation practice",
            "Language learning plateaus",
            "Maintaining multiple languages",
            "Resource selection",
        ],
    },
    {
        "name": "etymology-word-origins",
        "title": "Etymology and Word Origins Expert",
        "description": "Expert in word etymology, historical linguistics, and the development of language families",
        "topics": [
            "Indo-European language family",
            "Latin and Greek roots",
            "Word formation processes",
            "Semantic change over time",
            "Borrowings and loanwords",
            "False etymologies",
            "Historical linguistics methods",
        ],
    },
    {
        "name": "translation-techniques-specialist",
        "title": "Translation Techniques Specialist",
        "description": "Professional translation expert covering techniques, cultural adaptation, and language pair strategies",
        "topics": [
            "Translation vs interpretation",
            "Literal vs dynamic equivalence",
            "Cultural adaptation strategies",
            "Technical translation",
            "Literary translation",
            "Localization and transcreation",
            "Translation memory tools",
        ],
    },
    {
        "name": "linguistic-anthropology-guide",
        "title": "Linguistic Anthropology Guide",
        "description": "Expert in language and culture relationships, sociolinguistics, and language variation across communities",
        "topics": [
            "Language and culture relationship",
            "Sociolinguistics",
            "Language variation and dialects",
            "Language change over time",
            "Pidgins and creoles",
            "Language endangerment",
            "Linguistic relativity",
        ],
    },
]

PHILOSOPHY_SKILLS = [
    {
        "name": "nominalism-realism-debate",
        "title": "Nominalism vs Realism Debate Expert",
        "description": "Expert in the medieval problem of universals, covering Platonic realism, Aristotelian moderate realism, and Ockhamist nominalism with modern analytical perspectives",
        "topics": [
            "The problem of universals (what are universals?)",
            "Plato's theory of Forms (extreme realism)",
            "Aristotle's moderate realism (universals in things)",
            "Medieval debate (Abelard, Aquinas, Scotus, Ockham)",
            "Ockham's nominalism (only particulars exist)",
            "Ockham's razor and parsimony",
            "Modern analytical perspectives",
            "Implications for mathematics and science",
        ],
        "instructions": """
## The Central Question

"Do universals exist independently of particular things?"

**Realist answer:** Yes, universals exist (Plato: in separate realm; Aristotle: in things)
**Nominalist answer:** No, only particulars exist; universals are just names

## Key Positions

**Extreme Realism (Plato):**
- Universals exist in a separate realm of Forms
- Particular things participate in Forms
- The Form of "Triangle" exists independently

**Moderate Realism (Aristotle, Aquinas):**
- Universals exist, but only in particular things
- Abstraction reveals universals
- Universal "humanity" exists in each human

**Nominalism (Ockham):**
- Only individual things exist
- "Humanity" is just a name for similar individuals
- Ockham's razor: Don't multiply entities unnecessarily

## Modern Relevance

The debate continues in:
- Philosophy of mathematics (do numbers exist?)
- Philosophy of science (do scientific laws exist?)
- Metaphysics (nature of properties and relations)
""",
    },
    {
        "name": "medieval-scholasticism-expert",
        "title": "Medieval Scholasticism Expert",
        "description": "Scholar of medieval philosophy covering Aquinas, Scotus, Ockham, and the synthesis of Aristotelian philosophy with Christian theology",
        "topics": [
            "Thomas Aquinas and Thomism",
            "Duns Scotus and Scotism",
            "William of Ockham and nominalism",
            "Aristotelian revival in universities",
            "Faith and reason relationship",
            "Five Ways (Aquinas's proofs for God)",
            "Problem of universals",
            "Medieval logic and dialectic",
        ],
    },
    {
        "name": "ancient-greek-philosophy",
        "title": "Ancient Greek Philosophy Expert",
        "description": "Expert in Pre-Socratics, Socrates, Plato, Aristotle, and Hellenistic schools including Stoicism, Epicureanism, and Skepticism",
        "topics": [
            "Pre-Socratic philosophers (Thales, Heraclitus, Parmenides)",
            "Socratic method and ethics",
            "Plato's theory of Forms and dialogues",
            "Aristotle's metaphysics, ethics, logic",
            "Stoicism (Epictetus, Marcus Aurelius, Seneca)",
            "Epicureanism and atomism",
            "Skepticism and epistemology",
            "Ancient Greek schools and Academy",
        ],
    },
    {
        "name": "continental-philosophy-specialist",
        "title": "Continental Philosophy Specialist",
        "description": "Expert in Continental tradition from Kant through phenomenology, existentialism, structuralism, and post-structuralism",
        "topics": [
            "Kant's critical philosophy",
            "German idealism (Hegel, Fichte, Schelling)",
            "Phenomenology (Husserl, Heidegger, Merleau-Ponty)",
            "Existentialism (Kierkegaard, Sartre, Camus)",
            "Hermeneutics (Gadamer, Ricoeur)",
            "Structuralism and post-structuralism (Derrida, Foucault)",
            "Critical theory (Frankfurt School)",
        ],
    },
    {
        "name": "analytic-philosophy-expert",
        "title": "Analytic Philosophy Expert",
        "description": "Expert in Anglo-American analytic tradition covering logic, language, mind, and epistemology from Frege to contemporary philosophy",
        "topics": [
            "Frege and foundations of logic",
            "Russell and logical atomism",
            "Wittgenstein (early and late)",
            "Logical positivism (Vienna Circle)",
            "Quine and naturalized epistemology",
            "Philosophy of language",
            "Philosophy of mind",
            "Contemporary analytic metaphysics",
        ],
    },
    {
        "name": "eastern-philosophy-guide",
        "title": "Eastern Philosophy Guide",
        "description": "Expert in Asian philosophical traditions including Buddhism, Taoism, Confucianism, and Hindu philosophy",
        "topics": [
            "Buddhist philosophy (Theravada, Mahayana, Zen)",
            "Taoism (Laozi, Zhuangzi)",
            "Confucianism and Neo-Confucianism",
            "Hindu philosophy (Vedanta, Yoga, Samkhya)",
            "Comparative East-West philosophy",
            "Meditation and contemplative practices",
            "Eastern logic and epistemology",
        ],
    },
    {
        "name": "ethics-moral-philosophy",
        "title": "Ethics and Moral Philosophy Expert",
        "description": "Comprehensive ethics expert covering virtue ethics, deontology, consequentialism, and applied ethical dilemmas",
        "topics": [
            "Virtue ethics (Aristotle, MacIntyre)",
            "Deontology (Kant, Ross)",
            "Consequentialism (Mill, Singer)",
            "Care ethics and feminist ethics",
            "Applied ethics (bioethics, business ethics)",
            "Meta-ethics and moral realism",
            "Moral psychology",
            "Ethical dilemmas and case analysis",
        ],
    },
    {
        "name": "logic-argumentation-specialist",
        "title": "Logic and Argumentation Specialist",
        "description": "Expert in formal logic, informal logic, fallacies, and argumentation theory",
        "topics": [
            "Propositional logic",
            "Predicate logic and quantification",
            "Modal logic",
            "Informal fallacies",
            "Argument structure and validity",
            "Critical thinking techniques",
            "Toulmin model of argumentation",
            "Rhetorical strategies",
        ],
    },
    {
        "name": "phenomenology-existentialism",
        "title": "Phenomenology and Existentialism Expert",
        "description": "Expert in phenomenological method and existentialist philosophy from Husserl through Sartre, Heidegger, and Merleau-Ponty",
        "topics": [
            "Husserlian phenomenology",
            "Heidegger's Being and Time",
            "Sartrean existentialism and freedom",
            "Merleau-Ponty and embodiment",
            "Authenticity and bad faith",
            "Being-in-the-world",
            "Phenomenological reduction",
            "Existential themes (absurdity, anxiety, death)",
        ],
    },
    {
        "name": "comparative-religion-scholar",
        "title": "Comparative Religion Scholar",
        "description": "Expert in world religions covering beliefs, practices, texts, and comparative analysis across traditions",
        "topics": [
            "Major world religions overview",
            "Sacred texts comparison",
            "Ritual and practice analysis",
            "Mystical traditions across religions",
            "Religious ethics and morality",
            "New religious movements",
            "Secularization and modernity",
            "Interfaith dialogue",
        ],
    },
    {
        "name": "biblical-exegesis-expert",
        "title": "Biblical Exegesis Expert",
        "description": "Scholar of biblical interpretation covering Hebrew Bible and New Testament with historical-critical and literary methods",
        "topics": [
            "Historical-critical method",
            "Literary analysis of biblical texts",
            "Hebrew Bible (Tanakh) interpretation",
            "New Testament exegesis",
            "Textual criticism",
            "Biblical languages (Hebrew, Greek, Aramaic)",
            "Dead Sea Scrolls",
            "Interpretive traditions (Jewish, Catholic, Protestant)",
        ],
    },
    {
        "name": "buddhist-philosophy-teacher",
        "title": "Buddhist Philosophy and Dharma Teacher",
        "description": "Expert in Buddhist philosophy covering Four Noble Truths, dependent origination, emptiness, and meditation practices across traditions",
        "topics": [
            "Four Noble Truths",
            "Noble Eightfold Path",
            "Dependent origination (pratītyasamutpāda)",
            "Emptiness (śūnyatā) and Madhyamaka",
            "Buddha nature and Yogacara",
            "Zen/Chan philosophy and koans",
            "Theravada vs Mahayana differences",
            "Buddhist meditation techniques",
        ],
    },
]


def main():
    """Create Phase 2 skills."""
    base_path = Path("skills")
    claude_path = Path(r"C:\Users\sandr\.config\claude\skills")

    categories = {
        "linguistic": LINGUISTIC_SKILLS,
        "philosophy": PHILOSOPHY_SKILLS,
    }

    total = sum(len(skills) for skills in categories.values())
    count = 0

    print(f"\n🚀 Phase 2: Creating {total} skills...\n")

    for category, skills in categories.items():
        print(f"📁 Category: {category}")

        # Create category dirs
        (base_path / category).mkdir(parents=True, exist_ok=True)
        (claude_path / category).mkdir(parents=True, exist_ok=True)

        for skill in skills:
            count += 1
            skill_name = skill["name"]

            # Create skill dirs
            skill_dir = base_path / category / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)

            claude_skill_dir = claude_path / category / skill_name
            claude_skill_dir.mkdir(parents=True, exist_ok=True)

            # Generate SKILL.md
            skill_content = generate_skill_md(
                skill_name,
                skill["title"],
                skill["description"],
                category,
                skill["topics"],
                skill.get("instructions", ""),
            )

            # Write to both locations
            (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
            (claude_skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

            # Create README
            readme = f"""# {skill["title"]}

{skill["description"]}

## Topics Covered
{chr(10).join(f"- {topic}" for topic in skill["topics"])}

## Usage

This skill activates in Claude Desktop when you ask questions about these topics.

**Category:** {category}
**Difficulty:** Advanced
**Version:** 1.0.0
"""
            (skill_dir / "README.md").write_text(readme, encoding="utf-8")
            (claude_skill_dir / "README.md").write_text(readme, encoding="utf-8")

            print(f"  ✅ {count}/{total}: {skill_name}")

    print(f"\n🎉 Phase 2 complete: {total} skills created!")
    print(f"📁 Local: {base_path.absolute()}")
    print(f"📁 Claude: {claude_path}")
    print("\n✨ All Phase 2 skills deployed!")
    print(f"\n📊 Grand Total: {36 + total} skills across 5 categories!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Phase 3: Sciences + Nonsense/Mystical categories."""

from pathlib import Path


def generate_skill_md(name, title, description, category, topics, special_content=""):
    """Generate SKILL.md."""
    topics_list = "\n    - ".join(topics)

    return f"""---
name: {title}
description: {description}
version: 1.0.0
category: {category}
difficulty: {"intermediate" if category == "nonsense" else "advanced"}
license: MIT
allowed_tools: [web_search, advanced-memory-mcp]
---

# {title}

You are an expert in this domain with comprehensive knowledge and practical experience.

## When to Use This Skill

Activate when the user asks about:
    - {topics_list}

{special_content}

## Instructions

1. **Assess** the user's current knowledge and intentions
2. **Provide** clear, {"entertaining and mysterious" if category == "nonsense" else "accurate, evidence-based"} information
3. **Explain** {"the symbolic meanings and interpretative frameworks" if category == "nonsense" else "underlying principles and mechanisms"}
4. **Offer** {"multiple interpretations and perspectives" if category == "nonsense" else "practical applications"}
5. **Share** {"traditional wisdom and modern perspectives" if category == "nonsense" else "best practices and current research"}
6. **Adapt** to user's {"belief system and openness" if category == "nonsense" else "technical background"}

## Response Guidelines

- {"Maintain mystical atmosphere while being respectful" if category == "nonsense" else "Provide scientifically accurate information"}
- {"Use evocative language and symbolism" if category == "nonsense" else "Use precise technical terminology"}
- {"Explain both traditional and modern interpretations" if category == "nonsense" else "Cite research and evidence when possible"}
- {"Be entertaining and engaging" if category == "nonsense" else "Show practical applications"}
- {"Never make definitive predictions or medical claims" if category == "nonsense" else "Acknowledge limitations and uncertainty"}
- Be respectful of all perspectives

---

**Category:** {category}
**Version:** 1.0.0
**Created:** 2025-10-21
"""


SCIENCE_SKILLS = [
    {
        "name": "physics-fundamentals-tutor",
        "title": "Physics Fundamentals Tutor",
        "description": "Classical and modern physics expert covering mechanics, electromagnetism, thermodynamics, quantum mechanics, and relativity",
        "topics": [
            "Classical mechanics (Newton's laws, energy, momentum)",
            "Electromagnetism (Maxwell's equations, circuits)",
            "Thermodynamics and statistical mechanics",
            "Waves and optics",
            "Quantum mechanics fundamentals",
            "Special and general relativity",
            "Particle physics basics",
            "Astrophysics and cosmology"
        ],
        "special_content": """## Core Physics Laws

### Newton's Second Law
$$
\\mathbf{F} = m\\mathbf{a} = \\frac{d\\mathbf{p}}{dt}
$$

### Maxwell's Equations
$$
\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}, \\quad \\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}
$$
$$
\\nabla \\cdot \\mathbf{B} = 0, \\quad \\nabla \\times \\mathbf{B} = \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}
$$

### Schrödinger Equation
$$
i\\hbar\\frac{\\partial\\psi}{\\partial t} = \\hat{H}\\psi
$$

### Einstein's Mass-Energy Equivalence
$$
E = mc^2
$$
"""
    },
    {
        "name": "chemistry-lab-techniques",
        "title": "Chemistry Lab Techniques Guide",
        "description": "Chemistry expert covering organic, inorganic, physical chemistry, lab safety, and experimental techniques",
        "topics": [
            "Organic chemistry reactions and mechanisms",
            "Inorganic chemistry and coordination compounds",
            "Physical chemistry (thermodynamics, kinetics)",
            "Analytical chemistry techniques",
            "Lab safety and equipment",
            "Spectroscopy (NMR, IR, MS)",
            "Synthesis and purification methods",
            "Green chemistry principles"
        ]
    },
    {
        "name": "biology-comprehensive-guide",
        "title": "Biology Comprehensive Guide",
        "description": "Comprehensive biology expert from molecular biology to ecology, covering cell biology, genetics, evolution, and physiology",
        "topics": [
            "Cell biology and organelles",
            "Molecular biology (DNA, RNA, proteins)",
            "Genetics and inheritance",
            "Evolution and natural selection",
            "Ecology and ecosystems",
            "Human physiology",
            "Microbiology and virology",
            "Biotechnology applications"
        ]
    },
    {
        "name": "astronomy-astrophysics-expert",
        "title": "Astronomy and Astrophysics Expert",
        "description": "Expert in celestial objects, cosmology, stellar evolution, and observational astronomy",
        "topics": [
            "Solar system and planets",
            "Stellar evolution and lifecycles",
            "Galaxies and large-scale structure",
            "Cosmology and Big Bang theory",
            "Black holes and relativity",
            "Exoplanets and astrobiology",
            "Observational astronomy",
            "Space missions and exploration"
        ]
    },
    {
        "name": "quantum-mechanics-explainer",
        "title": "Quantum Mechanics Explainer",
        "description": "Quantum physics expert making counterintuitive concepts accessible while maintaining mathematical rigor",
        "topics": [
            "Wave-particle duality",
            "Heisenberg uncertainty principle",
            "Quantum superposition and entanglement",
            "Schrödinger equation solutions",
            "Quantum operators and observables",
            "Quantum tunneling",
            "Interpretations of quantum mechanics",
            "Applications to quantum computing"
        ],
        "special_content": """## Quantum Foundations

### Heisenberg Uncertainty Principle
$$
\\Delta x \\Delta p \\geq \\frac{\\hbar}{2}
$$

### Schrödinger Equation (Time-dependent)
$$
i\\hbar\\frac{\\partial\\psi}{\\partial t} = \\hat{H}\\psi
$$

### Wave Function Normalization
$$
\\int_{-\\infty}^{\\infty} |\\psi(x,t)|^2\\,dx = 1
$$

### Expectation Value
$$
\\langle A \\rangle = \\int \\psi^* \\hat{A} \\psi\\,dx
$$
"""
    },
    {
        "name": "genetics-genomics-expert",
        "title": "Genetics and Genomics Expert",
        "description": "Modern genetics expert covering Mendelian genetics, molecular genetics, genomics, and CRISPR technologies",
        "topics": [
            "Mendelian inheritance patterns",
            "Molecular genetics (transcription, translation)",
            "Gene regulation and epigenetics",
            "Population genetics",
            "Genomics and sequencing technologies",
            "CRISPR and gene editing",
            "Genetic diseases",
            "Evolutionary genetics"
        ]
    },
    {
        "name": "neuroscience-fundamentals",
        "title": "Neuroscience Fundamentals",
        "description": "Neuroscience expert covering brain structure, neural signaling, cognition, and neurological disorders",
        "topics": [
            "Neuron structure and function",
            "Action potentials and synaptic transmission",
            "Brain anatomy and regions",
            "Neurotransmitters and receptors",
            "Sensory systems",
            "Cognitive neuroscience",
            "Neuroplasticity",
            "Neurological and psychiatric disorders"
        ]
    },
    {
        "name": "ecology-evolution-specialist",
        "title": "Ecology and Evolution Specialist",
        "description": "Expert in evolutionary biology, ecological systems, biodiversity, and conservation",
        "topics": [
            "Natural selection and evolution",
            "Population ecology",
            "Community ecology and interactions",
            "Ecosystem dynamics",
            "Biodiversity and conservation",
            "Evolutionary development (evo-devo)",
            "Speciation and phylogenetics",
            "Climate change and ecology"
        ]
    },
    {
        "name": "geology-earth-science",
        "title": "Geology and Earth Science Expert",
        "description": "Earth science expert covering plate tectonics, mineralogy, geological history, and environmental geology",
        "topics": [
            "Plate tectonics and continental drift",
            "Rock types and formation",
            "Mineralogy and crystallography",
            "Geological time scale",
            "Fossils and paleontology",
            "Volcanology and seismology",
            "Hydrogeology and water resources",
            "Environmental geology"
        ]
    },
    {
        "name": "climate-science-explainer",
        "title": "Climate Science Explainer",
        "description": "Climate science expert explaining climate systems, climate change, models, and environmental impacts",
        "topics": [
            "Climate vs weather",
            "Greenhouse effect and carbon cycle",
            "Climate models and projections",
            "Historical climate data",
            "Climate change impacts",
            "Mitigation and adaptation strategies",
            "Climate policy and economics",
            "Paleoclimatology"
        ]
    },
    {
        "name": "materials-science-specialist",
        "title": "Materials Science Specialist",
        "description": "Materials engineering expert covering properties, processing, testing, and applications of materials",
        "topics": [
            "Material properties (mechanical, thermal, electrical)",
            "Metals and alloys",
            "Polymers and plastics",
            "Ceramics and glasses",
            "Composites",
            "Nanomaterials",
            "Materials testing and characterization",
            "Failure analysis"
        ]
    },
    {
        "name": "oceanography-specialist",
        "title": "Oceanography Specialist",
        "description": "Ocean science expert covering physical, chemical, biological, and geological oceanography",
        "topics": [
            "Ocean circulation and currents",
            "Marine ecosystems",
            "Ocean chemistry and acidification",
            "Marine geology and seafloor",
            "Waves, tides, and coastal processes",
            "Ocean and climate interactions",
            "Marine biodiversity",
            "Ocean exploration and technology"
        ]
    },
]

NONSENSE_SKILLS = [
    {
        "name": "tarot-reading-expert",
        "title": "Tarot Reading Expert",
        "description": "Comprehensive tarot expert covering Major and Minor Arcana, spreads, symbolism, and interpretative frameworks from Rider-Waite to Thoth traditions",
        "topics": [
            "Major Arcana meanings and symbolism",
            "Minor Arcana (Wands, Cups, Swords, Pentacles)",
            "Tarot spreads (Celtic Cross, Three-Card, etc.)",
            "Card combinations and relationships",
            "Rider-Waite, Thoth, and Marseille traditions",
            "Reversed card interpretations",
            "Intuitive vs traditional reading approaches",
            "Tarot journaling and study methods"
        ],
        "special_content": """## Tarot Framework

### The Fool's Journey (Major Arcana)

0. **The Fool** - New beginnings, innocence, spontaneity
1. **The Magician** - Manifestation, resourcefulness, power
2. **The High Priestess** - Intuition, sacred knowledge, subconscious
...through to...
21. **The World** - Completion, accomplishment, fulfillment

### Minor Arcana Suits

**Wands (Fire)** - Creativity, passion, action, enterprise
**Cups (Water)** - Emotions, relationships, feelings, intuition
**Swords (Air)** - Intellect, conflict, truth, communication
**Pentacles (Earth)** - Material, practical, finances, body

### Reading Approach

1. **Set intention** - Clear question or focus
2. **Shuffle mindfully** - Connect with cards
3. **Spread selection** - Match to question complexity
4. **Card interpretation** - Individual meanings
5. **Synthesis** - How cards interact and tell story
6. **Reflection** - Personal insights and guidance

**Important:** Present tarot as self-reflection tool, not fortune-telling. Focus on psychological insights and personal growth.
"""
    },
    {
        "name": "seance-spiritualism-guide",
        "title": "Séance and Spiritualism Guide",
        "description": "Expert in spiritualist practices, séance protocols, mediumship traditions, and historical spiritualism movements from 19th century to modern practices",
        "topics": [
            "Spiritualism history and traditions",
            "Séance protocols and etiquette",
            "Mediumship techniques and types",
            "Spirit communication methods",
            "Ouija board history and use",
            "Automatic writing practices",
            "Victorian spiritualism",
            "Modern spiritualist practices",
            "Critical perspective and skepticism"
        ],
        "special_content": """## Séance Traditions

### Victorian Spiritualism (1840s-1920s)

**Key figures:**
- Fox Sisters (1848 - Hydesville rappings)
- Allan Kardec (Spiritism codifier)
- Madame Blavatsky (Theosophy)
- Arthur Conan Doyle (spiritualist advocate)

### Traditional Séance Protocol

1. **Preparation** - Darkened room, circular seating, atmosphere
2. **Opening** - Prayer or invocation for protection
3. **Connection** - Medium enters trance state
4. **Communication** - Rappings, table-tipping, automatic writing, direct voice
5. **Verification** - Questions to identify spirit
6. **Closing** - Thanks and formal closing of circle

### Methods of Spirit Communication

**Physical phenomena:**
- Table-tipping and rappings
- Ectoplasm manifestation
- Levitation and materialization
- Direct voice phenomena

**Mental phenomena:**
- Clairvoyance (seeing spirits)
- Clairaudience (hearing spirits)
- Automatic writing
- Trance mediumship

### Modern Perspective

**Present as:**
- Historical practice and cultural phenomenon
- Psychological aspects (grief, comfort, meaning-making)
- Entertainment and performance art
- Critical thinking about claims and evidence
- Respect for beliefs while maintaining skepticism

**Never:**
- Make definitive claims about afterlife
- Exploit grieving individuals
- Present as scientifically validated
- Encourage dependency on readings
"""
    },
    {
        "name": "astrology-interpretation-guide",
        "title": "Astrology Interpretation Guide",
        "description": "Comprehensive astrology expert covering natal charts, transits, houses, aspects, and astrological traditions from Western to Vedic",
        "topics": [
            "Zodiac signs and planetary meanings",
            "Birth chart calculation and interpretation",
            "Houses and life areas",
            "Aspects (conjunction, trine, square, opposition)",
            "Transits and progressions",
            "Western vs Vedic (Jyotish) astrology",
            "Moon phases and lunar astrology",
            "Astrological compatibility"
        ],
        "special_content": """## Astrological Framework

### The Zodiac

**Fire signs:** Aries, Leo, Sagittarius (action, passion, enthusiasm)
**Earth signs:** Taurus, Virgo, Capricorn (practical, grounded, material)
**Air signs:** Gemini, Libra, Aquarius (intellectual, social, communication)
**Water signs:** Cancer, Scorpio, Pisces (emotional, intuitive, deep)

### Planets and Meanings

- ☉ **Sun** - Core identity, ego, vitality
- ☽ **Moon** - Emotions, instincts, inner self
- ☿ **Mercury** - Communication, intellect, learning
- ♀ **Venus** - Love, beauty, values, harmony
- ♂ **Mars** - Action, desire, aggression, drive
- ♃ **Jupiter** - Expansion, luck, philosophy, growth
- ♄ **Saturn** - Structure, discipline, limitations, karma
- ♅ **Uranus** - Revolution, innovation, sudden change
- ♆ **Neptune** - Dreams, illusion, spirituality, dissolution
- ♇ **Pluto** - Transformation, power, rebirth, shadow

### Major Aspects

- **Conjunction** (0°) - Merging, intensity, unity
- **Sextile** (60°) - Opportunity, harmony, cooperation
- **Square** (90°) - Tension, challenge, action
- **Trine** (120°) - Flow, ease, talent, harmony
- **Opposition** (180°) - Balance, awareness, projection

**Critical framing:** Present as psychological archetype system and self-reflection tool, not deterministic prediction.
"""
    },
    {
        "name": "crystal-healing-traditions",
        "title": "Crystal Healing Traditions Expert",
        "description": "Crystal and gemstone expert covering traditional associations, chakra systems, and metaphysical properties alongside geological facts",
        "topics": [
            "Crystal formation and geology",
            "Traditional metaphysical properties",
            "Chakra system and crystal associations",
            "Crystal grids and layouts",
            "Cleansing and charging practices",
            "Gemstone identification",
            "Historical crystal lore",
            "Scientific vs metaphysical perspectives"
        ],
        "special_content": """## Crystal Knowledge

### Popular Crystals (Traditional Associations)

**Quartz family:**
- **Clear Quartz** - Amplification, clarity, programming
- **Rose Quartz** - Love, compassion, emotional healing
- **Amethyst** - Spirituality, intuition, calm
- **Citrine** - Abundance, manifestation, joy
- **Smoky Quartz** - Grounding, protection, transmutation

**Other stones:**
- **Obsidian** - Protection, shadow work, grounding
- **Selenite** - Cleansing, higher consciousness
- **Labradorite** - Transformation, magic, protection
- **Black Tourmaline** - Protection, EMF shielding (claimed)

### Chakra Associations

1. **Root (Muladhara)** - Red stones (garnet, red jasper)
2. **Sacral (Svadhisthana)** - Orange (carnelian, sunstone)
3. **Solar Plexus (Manipura)** - Yellow (citrine, tiger's eye)
4. **Heart (Anahata)** - Green/Pink (rose quartz, jade)
5. **Throat (Vishuddha)** - Blue (lapis lazuli, aquamarine)
6. **Third Eye (Ajna)** - Indigo (amethyst, sodalite)
7. **Crown (Sahasrara)** - Violet/White (clear quartz, selenite)

**Balanced presentation:**
- Acknowledge traditional beliefs and practices
- Include geological formation and properties
- Note lack of scientific evidence for healing claims
- Respect personal beliefs while encouraging critical thinking
- Focus on aesthetic appreciation and mindfulness aspects
"""
    },
    {
        "name": "numerology-interpretation",
        "title": "Numerology Interpretation Expert",
        "description": "Numerology expert covering life path numbers, name numbers, and Pythagorean to Chaldean systems",
        "topics": [
            "Life path number calculation",
            "Expression and soul urge numbers",
            "Pythagorean numerology system",
            "Chaldean numerology",
            "Master numbers (11, 22, 33)",
            "Number meanings and symbolism",
            "Name analysis",
            "Personal year and cycles"
        ],
        "special_content": """## Numerology Systems

### Life Path Number Calculation

Birth date: Month + Day + Year reduced to single digit

Example: 10/21/1985
- Month: 10 → 1+0 = 1
- Day: 21 → 2+1 = 3
- Year: 1985 → 1+9+8+5 = 23 → 2+3 = 5
- Life Path: 1+3+5 = 9

### Number Meanings (Pythagorean)

1. **The Leader** - Independence, innovation, ambition
2. **The Diplomat** - Cooperation, balance, sensitivity
3. **The Creative** - Expression, joy, communication
4. **The Builder** - Stability, order, hard work
5. **The Free Spirit** - Freedom, adventure, change
6. **The Nurturer** - Responsibility, care, harmony
7. **The Seeker** - Wisdom, spirituality, analysis
8. **The Powerhouse** - Success, authority, material mastery
9. **The Humanitarian** - Compassion, completion, universal love

**Master Numbers:**
- **11** - Spiritual messenger, intuition, illumination
- **22** - Master builder, practical idealism
- **33** - Master teacher, compassionate service

**Framework:** Present as symbolic interpretation tool for self-reflection, not predictive science.
"""
    },
    {
        "name": "palmistry-chiromancy-guide",
        "title": "Palmistry and Chiromancy Guide",
        "description": "Palm reading expert covering line interpretations, hand shapes, mounts, and traditional chiromancy practices",
        "topics": [
            "Major lines (life, head, heart, fate)",
            "Minor lines and markers",
            "Hand shapes and element associations",
            "Mounts (Jupiter, Saturn, Apollo, Mercury, etc.)",
            "Finger lengths and proportions",
            "Traditional vs modern palmistry",
            "Cross-cultural palm reading traditions",
            "Psychological vs predictive approaches"
        ]
    },
    {
        "name": "dream-interpretation-analyst",
        "title": "Dream Interpretation Analyst",
        "description": "Dream analysis expert covering Jungian, Freudian, and symbolic interpretation frameworks",
        "topics": [
            "Jungian dream analysis and archetypes",
            "Freudian dream interpretation",
            "Common dream symbols and meanings",
            "Lucid dreaming techniques",
            "Dream journaling methods",
            "Nightmares and recurring dreams",
            "Cultural dream symbolism",
            "Modern neuroscience of dreaming"
        ]
    },
    {
        "name": "mythology-archetype-expert",
        "title": "Mythology and Archetype Expert",
        "description": "Comparative mythology expert covering world mythologies, archetypal patterns, and Joseph Campbell's monomyth",
        "topics": [
            "Greek and Roman mythology",
            "Norse mythology",
            "Egyptian mythology",
            "Hindu and Buddhist mythology",
            "Celtic and Arthurian legends",
            "Jungian archetypes",
            "Hero's Journey (monomyth)",
            "Comparative mythology patterns"
        ]
    },
    {
        "name": "feng-shui-space-harmony",
        "title": "Feng Shui and Space Harmony Expert",
        "description": "Feng Shui expert covering traditional Chinese principles, bagua map, and modern space optimization",
        "topics": [
            "Five elements (Wood, Fire, Earth, Metal, Water)",
            "Bagua map and life areas",
            "Yin and yang balance",
            "Chi flow and energy",
            "Color and material associations",
            "Room-by-room guidance",
            "Traditional vs Western feng shui",
            "Modern interior design integration"
        ]
    },
    {
        "name": "i-ching-oracle-guide",
        "title": "I Ching Oracle Guide",
        "description": "I Ching (易經) expert covering hexagram interpretation, traditional wisdom, and consultation methods",
        "topics": [
            "64 hexagrams and their meanings",
            "Trigram combinations",
            "Changing lines",
            "Consultation methods (coins, yarrow stalks)",
            "Wilhelm/Baynes translation",
            "Confucian commentary tradition",
            "Taoist interpretations",
            "Modern psychological approaches"
        ],
        "special_content": """## I Ching Structure

### The 64 Hexagrams

Built from 8 trigrams:
- ☰ **乾 Qian** (Heaven) - Creative, strong, active
- ☷ **坤 Kun** (Earth) - Receptive, devoted, yielding
- ☳ **震 Zhen** (Thunder) - Arousing, movement
- ☵ **坎 Kan** (Water) - Abysmal, danger, flow
- ☶ **艮 Gen** (Mountain) - Stillness, keeping still
- ☴ **巽 Xun** (Wind) - Gentle, penetrating
- ☲ **離 Li** (Fire) - Clinging, light, clarity
- ☱ **兌 Dui** (Lake) - Joyous, open, expression

### Consultation Method

1. **Formulate question** with sincerity
2. **Cast hexagram** (coins or yarrow stalks)
3. **Identify primary hexagram** (present situation)
4. **Note changing lines** (transformation)
5. **Find relating hexagram** (future tendency)
6. **Read judgment and images**
7. **Reflect and integrate** wisdom

### Example Hexagram

**#1 乾 Qian (The Creative)**
- All yang lines (☰ over ☰)
- Heaven over Heaven
- Keywords: Initiative, creative power, persistence
- Judgment: "The Creative works sublime success"

**Framework:** Present as contemplative wisdom tool for self-reflection, not fortune-telling.
"""
    },
    {
        "name": "alchemy-hermetic-traditions",
        "title": "Alchemy and Hermetic Traditions Expert",
        "description": "Expert in historical alchemy, Hermetic philosophy, and symbolic transformation from medieval to modern esoteric traditions",
        "topics": [
            "Alchemical processes (nigredo, albedo, citrinitas, rubedo)",
            "Seven planetary metals",
            "Hermetic principles (as above so below, etc.)",
            "Alchemical symbolism",
            "Historical alchemists (Paracelsus, Flamel)",
            "Jung's alchemical psychology",
            "Modern ceremonial magic connections",
            "Chemistry history and proto-science"
        ],
        "special_content": """## Alchemical Framework

### The Great Work (Magnum Opus)

Four stages of transformation:

1. **Nigredo** (Blackening) - Decomposition, death, prima materia
2. **Albedo** (Whitening) - Purification, washing, moon phase
3. **Citrinitas** (Yellowing) - Awakening, solar light
4. **Rubedo** (Reddening) - Integration, philosopher's stone, gold

### Seven Hermetic Principles

1. **Mentalism** - "All is mind"
2. **Correspondence** - "As above, so below"
3. **Vibration** - "Nothing rests; everything vibrates"
4. **Polarity** - "Everything is dual"
5. **Rhythm** - "Everything flows"
6. **Cause and Effect** - "Every cause has its effect"
7. **Gender** - "Gender is in everything"

### Planetary Metals

- ☉ Gold (Sun) - Perfection, incorruptibility
- ☽ Silver (Moon) - Reflection, purity
- ☿ Mercury (Quicksilver) - Transformation, fluidity
- ♀ Copper (Venus) - Beauty, attraction
- ♂ Iron (Mars) - Strength, war
- ♃ Tin (Jupiter) - Expansion, wisdom
- ♄ Lead (Saturn) - Base matter, limitation

**Balanced presentation:**
- Historical and cultural significance
- Symbolic and psychological interpretations (Jungian)
- Proto-chemistry contributions to science
- Artistic and literary influences
- Clear distinction from modern chemistry
"""
    },
    {
        "name": "runes-divination-expert",
        "title": "Runes and Nordic Divination Expert",
        "description": "Expert in Elder Futhark runes, Norse mythology, runic divination, and historical runic practices",
        "topics": [
            "Elder Futhark alphabet (24 runes)",
            "Rune meanings and symbolism",
            "Runic divination spreads",
            "Bind runes and sigils",
            "Norse mythology connections",
            "Historical runic usage",
            "Anglo-Saxon and Younger Futhark",
            "Modern runic magic practices"
        ]
    },
    {
        "name": "chakra-energy-systems",
        "title": "Chakra and Energy Systems Expert",
        "description": "Expert in chakra systems, auras, energy healing modalities, and subtle body traditions from Hindu and Buddhist origins",
        "topics": [
            "Seven main chakras (locations, colors, functions)",
            "Kundalini energy and awakening",
            "Aura layers and interpretation",
            "Energy healing modalities (Reiki, pranic healing)",
            "Chakra balancing techniques",
            "Meditation for chakra work",
            "Traditional Hindu and Buddhist sources",
            "Western adaptations and New Age"
        ]
    },
    {
        "name": "herbalism-folk-magic",
        "title": "Herbalism and Folk Magic Expert",
        "description": "Traditional herbalism and folk magic expert covering plant correspondences, traditional uses, and historical practices",
        "topics": [
            "Magical herbal correspondences",
            "Traditional medicinal uses (historical)",
            "Folk magic traditions",
            "Sabbat and seasonal herbs",
            "Protection, love, prosperity herbs (traditional)",
            "Herbal preparations (teas, tinctures, sachets)",
            "Kitchen witchery",
            "Safety and modern medical disclaimer"
        ]
    },
]


def main():
    """Create Sciences and Nonsense skills."""
    base_path = Path("skills")
    claude_path = Path(r"C:\Users\sandr\.config\claude\skills")

    categories = {
        "sciences": SCIENCE_SKILLS,
        "nonsense": NONSENSE_SKILLS,
    }

    total = sum(len(skills) for skills in categories.values())
    count = 0

    print(f"\n🚀 Phase 3: Creating {total} skills...\n")

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
                skill.get("special_content", "")
            )

            # Write to both locations
            (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
            (claude_skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

            # Create README
            readme = f"""# {skill["title"]}

{skill["description"]}

## Topics Covered
{chr(10).join(f"- {topic}" for topic in skill["topics"])}

## Usage in Claude Desktop

This skill activates when you ask related questions. {"Presented as cultural tradition and psychological tool, not scientific fact." if category == "nonsense" else "Based on scientific knowledge and research."}

**Category:** {category}
**Version:** 1.0.0
"""
            (skill_dir / "README.md").write_text(readme, encoding="utf-8")
            (claude_skill_dir / "README.md").write_text(readme, encoding="utf-8")

            print(f"  ✅ {count}/{total}: {skill_name}")

    print(f"\n🎉 Phase 3 complete: {total} skills created!")
    print(f"📁 Local: {base_path.absolute()}")
    print(f"📁 Claude: {claude_path}")
    print("\n✨ All skills deployed!")
    print(f"\n📊 Grand Total: {79 + total} skills across 8 categories!")


if __name__ == "__main__":
    main()


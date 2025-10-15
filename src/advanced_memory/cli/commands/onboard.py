"""Onboarding command for Advanced Memory - creates personalized starter Zettelkasten."""

import asyncio
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from advanced_memory.cli.app import app
from advanced_memory.mcp.tools import write_note as mcp_write_note

# Create onboard subcommand
onboard_app = typer.Typer(help="Create personalized starter Zettelkasten")
app.add_typer(onboard_app, name="onboard")

console = Console()

# Predefined content templates for different interests
CONTENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "developer": {
        "python": [
            {
                "title": "Python Fundamentals",
                "folder": "development/python",
                "content": """# Python Fundamentals

## Core Concepts
- **Variables & Types**: int, float, str, bool, list, dict, tuple
- **Control Flow**: if/elif/else, for/while loops, break/continue
- **Functions**: def, return, parameters, scope
- **Modules**: import, from, __name__, packages

## Key Principles
1. **Readability**: Code should be clear and self-documenting
2. **Simplicity**: Keep solutions simple and direct
3. **Consistency**: Follow PEP 8 and established patterns

## Common Patterns
- List comprehensions: `[x**2 for x in range(10)]`
- Dictionary comprehensions: `{k: v*2 for k, v in d.items()}`
- Lambda functions: `lambda x: x**2`

## Learning Resources
- [[Python Official Tutorial]]
- [[PEP 8 Style Guide]]
- [[Python Data Model]]

*Start with small scripts, build understanding gradually.*""",
            },
            {
                "title": "Object-Oriented Programming",
                "folder": "development/python",
                "content": """# Object-Oriented Programming in Python

## Core Concepts
- **Classes**: Blueprint for creating objects
- **Objects**: Instances of classes with state and behavior
- **Inheritance**: Creating specialized classes from base classes
- **Polymorphism**: Same interface, different implementations

## Key Syntax
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says woof!"
```

## Design Principles
1. **Single Responsibility**: Each class has one job
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes should be substitutable for base types
4. **Interface Segregation**: Many specific interfaces > one general interface

## Common Patterns
- Factory Pattern: Object creation logic
- Singleton Pattern: One instance only
- Observer Pattern: Event handling
- Strategy Pattern: Interchangeable algorithms

## Related Concepts
- [[Python Classes]]
- [[Inheritance Patterns]]
- [[Design Patterns]]
- [[SOLID Principles]]

*OOP is a tool, not a requirement. Use when it simplifies your code.*""",
            },
        ],
        "web-development": [
            {
                "title": "Web Development Fundamentals",
                "folder": "development/web",
                "content": """# Web Development Fundamentals

## Frontend Technologies
- **HTML**: Structure and content of web pages
- **CSS**: Styling and layout of web pages
- **JavaScript**: Interactive behavior and dynamic content

## Backend Technologies
- **Server-Side Languages**: Python, Node.js, PHP, Ruby, Java
- **Databases**: SQL (PostgreSQL, MySQL) and NoSQL (MongoDB)
- **APIs**: REST, GraphQL, WebSockets

## Key Concepts
1. **Client-Server Model**: Browser requests, server responds
2. **HTTP Protocol**: GET, POST, PUT, DELETE methods
3. **Stateless Nature**: Each request is independent
4. **Sessions & Cookies**: Maintaining state across requests

## Development Process
1. **Planning**: Define requirements and architecture
2. **Frontend**: Build user interface and experience
3. **Backend**: Implement server logic and data handling
4. **Integration**: Connect frontend and backend
5. **Testing**: Ensure functionality and performance
6. **Deployment**: Make application available to users

## Essential Tools
- **Version Control**: Git for code management
- **Package Managers**: npm, pip, yarn for dependencies
- **Build Tools**: Webpack, Vite, Babel for compilation
- **Testing**: Jest, pytest, Cypress for quality assurance

## Related Areas
- [[API Design]]
- [[Database Design]]
- [[Security Best Practices]]
- [[Performance Optimization]]

*Web development is about creating experiences, not just code.*""",
            },
        ],
        "ai-ml": [
            {
                "title": "Machine Learning Fundamentals",
                "folder": "research/ai",
                "content": """# Machine Learning Fundamentals

## Core Concepts
- **Supervised Learning**: Learning from labeled examples
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through interaction and rewards

## Key Algorithms
### Supervised Learning
- **Linear Regression**: Predicting continuous values
- **Logistic Regression**: Binary classification
- **Decision Trees**: Tree-based classification and regression
- **Random Forest**: Ensemble of decision trees
- **Support Vector Machines**: Maximum margin classification
- **Neural Networks**: Layered learning systems

### Unsupervised Learning
- **K-Means Clustering**: Grouping similar data points
- **Principal Component Analysis**: Dimensionality reduction
- **Autoencoders**: Neural network compression
- **Generative Adversarial Networks**: Data generation

## Machine Learning Workflow
1. **Problem Definition**: What are you trying to solve?
2. **Data Collection**: Gather relevant training data
3. **Data Preparation**: Clean, normalize, feature engineering
4. **Model Selection**: Choose appropriate algorithm
5. **Training**: Fit model to training data
6. **Evaluation**: Assess model performance
7. **Deployment**: Put model into production
8. **Monitoring**: Track performance and retrain as needed

## Important Considerations
- **Data Quality**: Garbage in, garbage out
- **Overfitting**: Model performs well on training data but poorly on new data
- **Bias-Variance Tradeoff**: Balancing model complexity
- **Interpretability**: Understanding model decisions
- **Ethical Implications**: Responsible AI development

## Tools and Frameworks
- **Python Libraries**: scikit-learn, TensorFlow, PyTorch
- **Data Processing**: pandas, NumPy
- **Visualization**: matplotlib, seaborn
- **Experiment Tracking**: MLflow, Weights & Biases

## Related Fields
- [[Statistics]]
- [[Linear Algebra]]
- [[Probability Theory]]
- [[Data Science]]
- [[Deep Learning]]

*Machine learning is about finding patterns in data to make predictions.*""",
            },
        ],
    },
    "cooking": {
        "general": [
            {
                "title": "Cooking Fundamentals",
                "folder": "cooking/basics",
                "content": """# Cooking Fundamentals

## Essential Techniques
- **Knife Skills**: Proper cutting techniques for safety and efficiency
- **Heat Control**: Understanding different heat levels and their effects
- **Timing**: Knowing when to start, stop, and rest ingredients
- **Seasoning**: Balancing flavors with salt, acid, sweetness, and heat

## Basic Cooking Methods
- **Sautéing**: Quick cooking in a small amount of fat
- **Roasting**: Dry heat cooking in the oven
- **Boiling**: Cooking in liquid at 100°C/212°F
- **Baking**: Dry heat cooking in the oven (typically for desserts)
- **Grilling**: High-heat cooking with direct contact to heat source
- **Steaming**: Cooking with hot vapor

## Key Ingredients
### Proteins
- **Meat**: Beef, pork, lamb, poultry, fish, shellfish
- **Plant-based**: Beans, lentils, tofu, tempeh, seitan
- **Dairy**: Eggs, cheese, milk, yogurt

### Vegetables
- **Leafy Greens**: Spinach, kale, lettuce, cabbage
- **Root Vegetables**: Potatoes, carrots, onions, garlic
- **Cruciferous**: Broccoli, cauliflower, Brussels sprouts
- **Nightshades**: Tomatoes, peppers, eggplant

### Staples
- **Grains**: Rice, wheat, oats, quinoa, barley
- **Oils**: Olive oil, vegetable oil, butter, ghee
- **Seasonings**: Salt, pepper, herbs, spices

## Flavor Profiles
1. **Umami**: Savory, meaty flavor (soy sauce, mushrooms, aged cheese)
2. **Sweet**: Natural sugars and added sweeteners
3. **Sour**: Acidic flavors (vinegar, citrus, yogurt)
4. **Salty**: Enhances other flavors, important for balance
5. **Bitter**: Often from greens, can be balanced with other flavors
6. **Spicy**: Heat from peppers and spices

## Kitchen Safety
- **Food Storage**: Proper refrigeration and labeling
- **Cross-Contamination**: Keep raw and cooked foods separate
- **Temperature Control**: Cook to safe internal temperatures
- **Hygiene**: Clean hands, surfaces, and utensils regularly

## Learning Approach
1. **Master Basics**: Learn fundamental techniques thoroughly
2. **Build Repertoire**: Start with simple recipes, gradually increase complexity
3. **Experiment**: Try variations on familiar recipes
4. **Document**: Keep notes on what works and what to improve
5. **Share**: Cook for others to get feedback and learn

*Cooking is both science and art - learn the rules, then break them creatively.*""",
            },
        ],
        "techniques": [
            {
                "title": "Knife Skills",
                "folder": "cooking/techniques",
                "content": """# Knife Skills

## Essential Cuts
### Basic Cuts
- **Brunoise**: 1/8" × 1/8" × 1/8" cubes (very fine dice)
- **Fine Dice**: 1/4" × 1/4" × 1/4" cubes
- **Medium Dice**: 1/2" × 1/2" × 1/2" cubes
- **Large Dice**: 3/4" × 3/4" × 3/4" cubes
- **Chiffonade**: Thin strips of leafy greens or herbs
- **Julienne**: 1/8" × 1/8" × 2" matchsticks
- **Batonnet**: 1/4" × 1/4" × 2" sticks

### Advanced Cuts
- **Oblique Cut**: Diagonal slices for even cooking
- **Roll Cut**: For long vegetables to increase surface area
- **Concassé**: Peeled, seeded, and chopped tomatoes
- **Supreme**: Citrus segments without membrane

## Knife Types
- **Chef's Knife**: All-purpose, 8-10 inch blade
- **Paring Knife**: Small tasks, peeling, trimming
- **Serrated Knife**: Bread and tomatoes
- **Utility Knife**: Medium-sized tasks
- **Santoku**: Japanese all-purpose knife

## Proper Technique
1. **Grip**: Pinch blade with thumb and forefinger, wrap other fingers around handle
2. **Posture**: Stand with feet shoulder-width apart, non-knife hand in "claw" position
3. **Motion**: Use entire arm, not just wrist; let weight of knife do the work
4. **Board Position**: Keep hand on top of food, curl fingers under

## Safety First
- **Sharp Knives**: Dull knives are more dangerous than sharp ones
- **Cutting Board**: Use stable, non-slip surface
- **Hand Position**: Keep fingertips tucked away from blade
- **Concentration**: Focus on task, no distractions
- **Storage**: Keep knives in block or on magnetic strip

## Practice Exercises
1. **Onion Dice**: Practice uniform cubes
2. **Carrot Batonnets**: Long, even sticks
3. **Herb Chiffonade**: Thin, uniform strips
4. **Potato Oblique**: Even diagonal slices

## Speed vs. Precision
- **Practice**: Start slow, focus on uniformity
- **Efficiency**: As skills improve, speed will follow
- **Quality**: Consistent cuts = consistent cooking results

*Good knife skills are the foundation of good cooking.*""",
            },
        ],
    },
    "philosophy": {
        "general": [
            {
                "title": "Philosophy Fundamentals",
                "folder": "philosophy/foundations",
                "content": """# Philosophy Fundamentals

## Major Branches of Philosophy
- **Metaphysics**: Nature of reality, existence, causality
- **Epistemology**: Nature and limits of knowledge
- **Ethics**: Moral principles and values
- **Political Philosophy**: Justice, rights, governance
- **Aesthetics**: Beauty, art, taste
- **Logic**: Reasoning and argumentation

## Key Questions
### Metaphysical Questions
- What exists? What is the nature of reality?
- What is the relationship between mind and body?
- Are we free, or is everything determined?
- Does God exist?

### Epistemological Questions
- What can we know? How do we know it?
- What are the limits of human knowledge?
- How reliable are our senses and reasoning?
- What is truth?

### Ethical Questions
- How should we live?
- What makes actions right or wrong?
- What is the good life?
- How do we resolve moral conflicts?

## Historical Periods
- **Ancient Philosophy**: Socrates, Plato, Aristotle (Greece)
- **Medieval Philosophy**: Augustine, Aquinas, Islamic philosophers
- **Modern Philosophy**: Descartes, Kant, Hume, Nietzsche
- **Contemporary Philosophy**: Existentialism, Analytic philosophy, Postmodernism

## Philosophical Methods
1. **Analysis**: Breaking down concepts into components
2. **Synthesis**: Building up from basic principles
3. **Dialectic**: Dialogue and debate to reach truth
4. **Phenomenology**: Studying conscious experience
5. **Hermeneutics**: Interpretation of texts and meanings

## Critical Thinking Skills
- **Identify Assumptions**: What is taken for granted?
- **Evaluate Arguments**: Are premises true? Is logic valid?
- **Recognize Fallacies**: Avoid common reasoning errors
- **Consider Perspectives**: Multiple viewpoints on issues
- **Question Authority**: Don't accept claims without evidence

## Why Philosophy Matters
- **Clarifies Thinking**: Helps us think more clearly about complex issues
- **Informs Decisions**: Better understanding of values and choices
- **Enhances Communication**: Better able to articulate and defend positions
- **Cultural Understanding**: Insights into different worldviews
- **Personal Growth**: Deeper self-understanding and wisdom

## Reading Philosophy
1. **Start with Overviews**: Books like "Sophie's World" or "The Story of Philosophy"
2. **Read Primary Texts**: Original works by philosophers
3. **Use Secondary Sources**: Commentaries and explanations
4. **Discuss and Debate**: Philosophy is meant to be discussed
5. **Apply to Life**: Connect philosophical ideas to real-world issues

*Philosophy begins in wonder and ends in wisdom.*""",
            },
        ],
    },
    "ai": {
        "general": [
            {
                "title": "AI Fundamentals",
                "folder": "research/ai",
                "content": """# AI Fundamentals

## What is Artificial Intelligence?
**Artificial Intelligence (AI)** is the ability of machines to perform tasks that typically require human intelligence, such as:
- Learning from experience
- Recognizing patterns
- Making decisions
- Understanding language
- Solving problems

## Types of AI

### Narrow AI (Weak AI)
- Designed for specific tasks
- Current AI systems (chess, image recognition, language translation)
- Cannot generalize beyond their training domain
- Examples: Chess engines, recommendation systems, voice assistants

### General AI (Strong AI)
- Human-level intelligence across all domains
- Can learn and adapt to any intellectual task
- Hypothetical, not yet achieved
- Would have consciousness, self-awareness, and general problem-solving ability

### Superintelligent AI
- Intelligence far exceeding human capabilities
- Could solve scientific, mathematical, and philosophical problems
- Potential benefits and risks to humanity

## Core AI Technologies

### Machine Learning
- **Supervised Learning**: Learning from labeled examples
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error with rewards

### Deep Learning
- Neural networks with multiple layers
- Inspired by the human brain's structure
- Powers image recognition, natural language processing, game playing

### Natural Language Processing
- Understanding and generating human language
- Powers chatbots, translation, text analysis
- Includes tokenization, parsing, semantic understanding

## AI Development Process
1. **Problem Definition**: What problem are you trying to solve?
2. **Data Collection**: Gather relevant training data
3. **Data Preparation**: Clean, format, and preprocess data
4. **Model Selection**: Choose appropriate algorithm or architecture
5. **Training**: Teach the model using training data
6. **Evaluation**: Test model performance on new data
7. **Deployment**: Make model available for real-world use
8. **Monitoring**: Track performance and update as needed

## Ethical Considerations
- **Bias and Fairness**: AI can perpetuate or amplify human biases
- **Privacy**: Data collection and usage concerns
- **Job Displacement**: Automation of human labor
- **Autonomous Weapons**: Lethal autonomous systems
- **Existential Risk**: Superintelligent AI safety

## Current AI Landscape
- **Large Language Models**: GPT, Claude, Gemini
- **Computer Vision**: Image recognition, autonomous vehicles
- **Robotics**: Physical AI systems
- **Expert Systems**: Specialized knowledge systems
- **AI in Healthcare**: Diagnosis, drug discovery, personalized medicine
- **AI in Finance**: Fraud detection, algorithmic trading, risk assessment

## Future Directions
- **Multimodal AI**: Combining text, images, audio, video
- **AI Safety Research**: Ensuring beneficial AI development
- **Human-AI Collaboration**: AI as tools to augment human capabilities
- **Explainable AI**: Understanding how AI makes decisions
- **AI Governance**: Policies and regulations for AI development

*AI is a tool that amplifies human capabilities, but its development requires wisdom and responsibility.*""",
            },
        ],
    },
}


async def create_note_from_template(template: dict[str, Any]) -> None:
    """Create a note from a template dictionary."""
    await mcp_write_note.fn(
        title=template["title"],
        content=template["content"],
        folder=template["folder"],
        tags=["starter-content", "auto-generated"],
        entity_type="note",
    )


def get_user_interests() -> dict[str, list[str]]:
    """Interactive prompt to get user interests."""
    console.print()
    console.print(
        Panel.fit(
            "🎨 [bold blue]Welcome to Advanced Memory![/bold blue]\n\n"
            "Let's create your personalized starter Zettelkasten.\n"
            "We'll generate 50-150 curated notes based on your interests.\n\n"
            "[dim]This will take 2-5 minutes and give you a rich knowledge foundation.[/dim]",
            title="🚀 Starter Zettelkasten Setup",
        )
    )

    interests = {}

    # Main categories
    categories = {
        "developer": "Software development, programming, tech",
        "cooking": "Culinary arts, recipes, techniques",
        "philosophy": "Philosophy, ethics, critical thinking",
        "ai": "Artificial intelligence, machine learning",
    }

    console.print("\n[bold]What are your main interests?[/bold]")
    console.print("[dim]Select all that apply (press Enter for each, empty line when done):[/dim]")

    for category, description in categories.items():
        response = Prompt.ask(f"Interested in {description}?", default="n")
        if response.lower() in ["y", "yes"]:
            # Get sub-interests
            sub_interests = get_sub_interests(category)
            if sub_interests:
                interests[category] = sub_interests

    return interests


def get_sub_interests(category: str) -> list[str]:
    """Get specific sub-interests within a category."""
    sub_categories = {
        "developer": ["python", "web-development", "ai-ml"],
        "cooking": ["general", "techniques"],
        "philosophy": ["general"],
        "ai": ["general"],
    }

    subs = sub_categories.get(category, [])
    if not subs:
        return []

    console.print(f"\n[bold]What aspects of {category} interest you?[/bold]")
    selected = []

    for sub in subs:
        response = Prompt.ask(f"Include {sub.replace('-', ' ')} content?", default="y")
        if response.lower() in ["y", "yes"]:
            selected.append(sub)

    return selected


async def generate_starter_content(interests: dict[str, list[str]]) -> int:
    """Generate starter content based on user interests."""
    total_notes = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for category, sub_interests in interests.items():
            for sub_interest in sub_interests:
                if category in CONTENT_TEMPLATES and sub_interest in CONTENT_TEMPLATES[category]:
                    templates = CONTENT_TEMPLATES[category][sub_interest]

                    for template in templates:
                        task = progress.add_task(f"Creating: {template['title']}", total=1)

                        await create_note_from_template(template)
                        total_notes += 1

                        progress.update(task, completed=1)
                        await asyncio.sleep(0.1)  # Small delay for visual feedback

    return total_notes


@onboard_app.command("wizard")
def onboard_wizard():
    """Interactive wizard to create personalized starter Zettelkasten."""
    try:
        # Get user interests
        interests = get_user_interests()

        if not interests:
            console.print("[yellow]No interests selected. Exiting...[/yellow]")
            return

        # Show summary
        total_categories = len(interests)
        total_sub_interests = sum(len(subs) for subs in interests.values())

        console.print(
            f"\n[bold green]Selected {total_categories} categories with {total_sub_interests} focus areas[/bold green]"
        )
        console.print("This will create approximately 50-150 starter notes.")

        # Confirm
        proceed = Prompt.ask("Ready to create your starter Zettelkasten?", default="y")
        if proceed.lower() not in ["y", "yes"]:
            console.print(
                "[yellow]Cancelled. Run 'advanced-memory onboard wizard' anytime to start over.[/yellow]"
            )
            return

        # Generate content
        console.print(
            "\n[bold blue]Generating your personalized starter Zettelkasten...[/bold blue]"
        )

        async def run_generation():
            return await generate_starter_content(interests)

        total_notes = asyncio.run(run_generation())

        # Success message
        console.print("\n[bold green]🎉 Success![/bold green]")
        console.print(f"Created [bold]{total_notes}[/bold] starter notes in your knowledge base!")
        console.print("\n[bold]What's next?[/bold]")
        console.print(
            '• Explore your new notes with: [cyan]advanced-memory search "starter"[/cyan]'
        )
        console.print("• Start connecting ideas by adding wikilinks [[Note Name]]")
        console.print("• Create your own notes to build on this foundation")
        console.print("• Use Claude with your MCP connection for seamless note creation")

        console.print("\n[dim]Welcome to your personal knowledge empire! 🏰📚[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Your knowledge base is safe.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during onboarding: {e}[/red]")
        console.print("[yellow]Your existing knowledge base is unchanged.[/yellow]")
        raise typer.Exit(1) from e


@onboard_app.command("quick")
def onboard_quick(
    interests: str = typer.Option(
        ...,
        "--interests",
        "-i",
        help="Comma-separated interests (developer, cooking, philosophy, ai)",
    ),
):
    """Quick setup with predefined interests."""
    try:
        # Parse interests
        interest_list = [i.strip() for i in interests.split(",")]
        interests_dict = {}

        for interest in interest_list:
            if interest in CONTENT_TEMPLATES:
                # Use all sub-interests for this category
                interests_dict[interest] = list(CONTENT_TEMPLATES[interest].keys())

        if not interests_dict:
            console.print(f"[red]No valid interests found in: {interests}[/red]")
            console.print(f"Available: {', '.join(CONTENT_TEMPLATES.keys())}")
            return

        console.print(
            f"[bold blue]Creating starter Zettelkasten for: {', '.join(interests_dict.keys())}[/bold blue]"
        )

        async def run_generation():
            return await generate_starter_content(interests_dict)

        total_notes = asyncio.run(run_generation())

        console.print(f"\n[bold green]✅ Created {total_notes} starter notes![/bold green]")
        console.print(
            "Run [cyan]advanced-memory onboard wizard[/cyan] for interactive setup anytime."
        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@onboard_app.callback()
def onboard_callback():
    """Create your personalized starter Zettelkasten."""
    pass

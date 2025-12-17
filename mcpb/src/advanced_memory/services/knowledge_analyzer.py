"""Knowledge analyzer service for smart onboarding and personalized recommendations.

This service analyzes a user's existing knowledge base to detect topics, skill levels,
knowledge gaps, and provides personalized template recommendations.
"""

from collections import Counter
from typing import Any

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.tools.utils import call_get


class KnowledgeAnalyzer:
    """Analyzes existing knowledge base for smart recommendations."""

    # Topic keywords for detection
    TOPIC_KEYWORDS = {
        "python": ["python", "django", "flask", "fastapi", "asyncio", "pandas", "numpy"],
        "javascript": ["javascript", "typescript", "node", "react", "vue", "next"],
        "devops": ["docker", "kubernetes", "ci/cd", "terraform", "aws", "azure", "deploy"],
        "data-science": ["machine learning", "ml", "data", "statistics", "numpy", "pandas"],
        "git": ["git", "github", "commit", "branch", "merge", "pull request"],
        "testing": ["test", "pytest", "unittest", "tdd", "testing"],
        "web": ["web", "html", "css", "frontend", "backend", "api"],
        "design": ["design", "ui", "ux", "figma", "user experience"],
        "product": ["product", "roadmap", "okr", "metrics", "strategy"],
        "business": ["business", "startup", "revenue", "marketing"],
    }

    # Skill level indicators
    BEGINNER_INDICATORS = ["tutorial", "introduction", "basics", "getting started", "fundamentals"]
    INTERMEDIATE_INDICATORS = ["advanced", "deep dive", "patterns", "best practices"]
    EXPERT_INDICATORS = ["architecture", "optimization", "performance", "internals", "expert"]

    async def analyze_knowledge_base(self, project: str) -> dict[str, Any]:
        """Analyze user's knowledge base for personalization.

        Args:
            project: Project name to analyze

        Returns:
            Dictionary with analysis results including topics, skill level, gaps
        """
        try:
            # Get all entities from project
            response = await call_get(client, f"/{project}/entities")
            entities_data = response.json()
            entities = entities_data.get("entities", [])

            if not entities:
                return {
                    "total_notes": 0,
                    "topics": [],
                    "skill_level": "beginner",
                    "gaps": [],
                    "recommendations": self._get_beginner_recommendations(),
                    "learning_style": "unknown",
                }

            # Extract analysis
            topics = self._detect_topics(entities)
            skill_level = self._detect_skill_level(entities)
            gaps = self._identify_gaps(topics)
            learning_style = self._detect_learning_style(entities)

            return {
                "total_notes": len(entities),
                "topics": topics,
                "skill_level": skill_level,
                "gaps": gaps,
                "recommendations": self._get_recommendations(topics, skill_level, gaps),
                "learning_style": learning_style,
                "coverage": self._calculate_coverage(topics),
            }

        except Exception as e:
            logger.error(f"Error analyzing knowledge base: {e}")
            return {
                "total_notes": 0,
                "topics": [],
                "skill_level": "beginner",
                "gaps": [],
                "recommendations": self._get_beginner_recommendations(),
                "learning_style": "unknown",
                "error": str(e),
            }

    def _detect_topics(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect topics from entity content.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of detected topics with confidence scores
        """
        topic_counts: Counter = Counter()

        # Analyze all entity content
        for entity in entities:
            content = entity.get("title", "").lower() + " " + entity.get("content", "").lower()

            for topic, keywords in self.TOPIC_KEYWORDS.items():
                matches = sum(1 for keyword in keywords if keyword in content)
                if matches > 0:
                    topic_counts[topic] += matches

        # Convert to topics with confidence
        total_matches = sum(topic_counts.values()) or 1
        topics = [
            {
                "topic": topic,
                "count": count,
                "confidence": round(count / total_matches, 2),
            }
            for topic, count in topic_counts.most_common(10)
        ]

        return topics

    def _detect_skill_level(self, entities: list[dict[str, Any]]) -> str:
        """Detect user's overall skill level.

        Args:
            entities: List of entity dictionaries

        Returns:
            Skill level: 'beginner', 'intermediate', or 'advanced'
        """
        beginner_count = 0
        intermediate_count = 0
        expert_count = 0

        for entity in entities:
            content = entity.get("title", "").lower() + " " + entity.get("content", "").lower()

            # Count indicators
            for indicator in self.BEGINNER_INDICATORS:
                if indicator in content:
                    beginner_count += 1

            for indicator in self.INTERMEDIATE_INDICATORS:
                if indicator in content:
                    intermediate_count += 1

            for indicator in self.EXPERT_INDICATORS:
                if indicator in content:
                    expert_count += 1

        # Determine level based on counts
        total = beginner_count + intermediate_count + expert_count

        if total == 0:
            # No clear indicators, check note count and complexity
            return "intermediate" if len(entities) > 20 else "beginner"

        # Calculate percentages
        expert_pct = expert_count / total
        intermediate_pct = intermediate_count / total

        if expert_pct > 0.3:
            return "advanced"
        elif intermediate_pct > 0.4:
            return "intermediate"
        else:
            return "beginner"

    def _identify_gaps(self, topics: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Identify knowledge gaps based on detected topics.

        Args:
            topics: List of detected topics

        Returns:
            List of gap dictionaries with recommendations
        """
        detected_topic_names = {t["topic"] for t in topics}
        gaps = []

        # Python-related gaps
        if "python" in detected_topic_names:
            if "testing" not in detected_topic_names:
                gaps.append(
                    {
                        "gap": "testing",
                        "reason": "You have Python knowledge but no testing coverage",
                        "recommendation": "Add testing fundamentals to ensure code quality",
                    }
                )
            if "git" not in detected_topic_names:
                gaps.append(
                    {
                        "gap": "git",
                        "reason": "Version control is essential for Python development",
                        "recommendation": "Learn Git for code management",
                    }
                )

        # Web development gaps
        if "javascript" in detected_topic_names or "web" in detected_topic_names:
            if "design" not in detected_topic_names:
                gaps.append(
                    {
                        "gap": "ui-ux-design",
                        "reason": "Web development benefits from design knowledge",
                        "recommendation": "Add UI/UX fundamentals for better interfaces",
                    }
                )

        # DevOps gaps
        if "python" in detected_topic_names or "javascript" in detected_topic_names:
            if "devops" not in detected_topic_names:
                gaps.append(
                    {
                        "gap": "devops",
                        "reason": "Deployment and operations complete the development cycle",
                        "recommendation": "Learn Docker and CI/CD for professional workflows",
                    }
                )

        # Data science gaps
        if "python" in detected_topic_names and "data-science" not in detected_topic_names:
            gaps.append(
                {
                    "gap": "data-science",
                    "reason": "Python is widely used in data science",
                    "recommendation": "Explore machine learning and data analysis",
                }
            )

        return gaps[:5]  # Top 5 gaps

    def _detect_learning_style(self, entities: list[dict[str, Any]]) -> str:
        """Detect user's learning style from note patterns.

        Args:
            entities: List of entity dictionaries

        Returns:
            Learning style: 'practical', 'theoretical', or 'balanced'
        """
        code_count = 0
        theory_count = 0

        for entity in entities:
            content = entity.get("content", "")

            # Count code blocks
            code_count += content.count("```")

            # Count theoretical indicators
            theory_words = ["definition", "concept", "theory", "principle", "philosophy"]
            theory_count += sum(1 for word in theory_words if word in content.lower())

        if code_count > theory_count * 1.5:
            return "practical"
        elif theory_count > code_count * 1.5:
            return "theoretical"
        else:
            return "balanced"

    def _calculate_coverage(self, topics: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate knowledge coverage by category.

        Args:
            topics: Detected topics

        Returns:
            Dictionary of category -> coverage percentage
        """
        coverage = {
            "developer": 0.0,
            "devops": 0.0,
            "data-scientist": 0.0,
            "design": 0.0,
            "product": 0.0,
            "business": 0.0,
        }

        for topic_info in topics:
            topic = topic_info["topic"]
            confidence = topic_info["confidence"]

            # Map topics to categories
            if topic in ["python", "javascript", "web", "git", "testing"]:
                coverage["developer"] += confidence
            elif topic in ["devops"]:
                coverage["devops"] += confidence
            elif topic in ["data-science"]:
                coverage["data-scientist"] += confidence
            elif topic in ["design"]:
                coverage["design"] += confidence
            elif topic in ["product"]:
                coverage["product"] += confidence
            elif topic in ["business"]:
                coverage["business"] += confidence

        # Normalize to percentages (cap at 100%)
        return {cat: min(score * 100, 100) for cat, score in coverage.items()}

    def _get_recommendations(
        self, topics: list[dict[str, Any]], skill_level: str, gaps: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        """Generate personalized recommendations.

        Args:
            topics: Detected topics
            skill_level: User's skill level
            gaps: Identified knowledge gaps

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # Add gap-filling recommendations
        for gap in gaps[:3]:  # Top 3 gaps
            recommendations.append(
                {
                    "type": "gap",
                    "priority": "high",
                    "title": f"Fill knowledge gap: {gap['gap']}",
                    "reason": gap["reason"],
                    "action": gap["recommendation"],
                }
            )

        # Add skill-appropriate recommendations
        if skill_level == "beginner":
            recommendations.extend(
                [
                    {
                        "type": "foundation",
                        "priority": "high",
                        "title": "Build strong fundamentals",
                        "reason": "Strong foundation accelerates future learning",
                        "action": "Focus on core concepts before advanced topics",
                    }
                ]
            )
        elif skill_level == "intermediate":
            recommendations.extend(
                [
                    {
                        "type": "expansion",
                        "priority": "medium",
                        "title": "Expand into related areas",
                        "reason": "Broaden expertise across domains",
                        "action": "Explore complementary topics",
                    }
                ]
            )
        else:  # advanced
            recommendations.extend(
                [
                    {
                        "type": "depth",
                        "priority": "medium",
                        "title": "Deepen expertise in specialization",
                        "reason": "Master advanced topics in your domain",
                        "action": "Explore expert-level templates",
                    }
                ]
            )

        return recommendations[:5]  # Top 5 recommendations

    def _get_beginner_recommendations(self) -> list[dict[str, Any]]:
        """Get default recommendations for beginners.

        Returns:
            List of beginner-friendly recommendations
        """
        return [
            {
                "type": "start",
                "priority": "high",
                "title": "Start with Developer Fundamentals",
                "reason": "Most universal and practical starting point",
                "action": "Generate python-core templates",
            },
            {
                "type": "start",
                "priority": "high",
                "title": "Learn Version Control",
                "reason": "Essential for all knowledge workers",
                "action": "Generate git templates",
            },
            {
                "type": "start",
                "priority": "medium",
                "title": "Build Productivity System",
                "reason": "Effective note-taking accelerates learning",
                "action": "Generate knowledge-worker templates",
            },
        ]

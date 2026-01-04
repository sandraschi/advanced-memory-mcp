# Zettelmaker Onboarding Dashboard

**Version:** 1.0
**Created:** October 16, 2025
**Integration:** Phase 4 (Smart Onboarding) Enhancement
**Platforms:** CLI, Web, Desktop (Advanced Memory Pro)

---

## Vision

Create a **visual, interactive onboarding dashboard** that tracks user progress, visualizes their knowledge graph, suggests next steps, and gamifies the learning experience across CLI, web, and desktop interfaces.

---

## Multi-Platform Dashboard

### 1. CLI Dashboard (Rich Terminal UI) 🖥️

**Implementation:** Uses `rich` library for beautiful terminal visualization

```python
advanced-memory onboard dashboard
```

**Features:**

#### Main Dashboard View
```
╔═══════════════════════════════════════════════════════════════╗
║         🚀 Zettelmaker Onboarding Dashboard                   ║
╚═══════════════════════════════════════════════════════════════╝

┌─ Your Progress ────────────────────────────────────────────────┐
│  📊 Overall Completion: ████████████░░░░░░░░ 60%              │
│  📝 Notes Created: 42 / 70 recommended                         │
│  🔗 Connections Made: 156 links                                │
│  📈 Knowledge Score: 847 / 1000                                │
└────────────────────────────────────────────────────────────────┘

┌─ Knowledge Graph ──────────────────────────────────────────────┐
│                                                                │
│       [Python] ──────┬────── [FastAPI]                        │
│          │           │          │                              │
│          │           └──── [Async]                             │
│          │                     │                               │
│       [Testing] ──────────── [Git]                            │
│          │                                                     │
│       [CI/CD] ────── [Docker]                                 │
│                                                                │
│  🎯 Clusters: 3 │ 🔓 Orphans: 2 │ 🌟 Central Concepts: 5      │
└────────────────────────────────────────────────────────────────┘

┌─ Current Learning Path ────────────────────────────────────────┐
│  ✅ Python Fundamentals                                        │
│  ✅ Git Basics                                                 │
│  ✅ Testing Fundamentals                                       │
│  🔄 Async Programming (In Progress - 40%)                     │
│  🔒 FastAPI Basics (Unlock: Complete Async)                   │
│  🔒 API Testing (Unlock: Complete FastAPI)                    │
└────────────────────────────────────────────────────────────────┘

┌─ Recommended Next Steps ───────────────────────────────────────┐
│  1. 💡 Complete "Async Programming" module (3 notes left)     │
│  2. 🔗 Connect "Testing" with "CI/CD" concepts                 │
│  3. 📦 Install "Web Development Starter Pack" from marketplace │
│  4. 🎯 Fill knowledge gap: Type Hints & Annotations            │
└────────────────────────────────────────────────────────────────┘

┌─ Achievements ─────────────────────────────────────────────────┐
│  🏆 First 10 Notes       🎯 Knowledge Explorer                │
│  🔗 Connector (50+ links) 🌟 Python Enthusiast                │
│  📚 Template Master      🚀 Fast Learner                      │
└────────────────────────────────────────────────────────────────┘

┌─ Stats & Insights ─────────────────────────────────────────────┐
│  📅 Days Active: 7        │  ⚡ Notes/Day: 6.0                │
│  🎓 Skill Level: Intermediate │ 🔥 Streak: 5 days             │
│  📊 Coverage: Python 80%, Git 60%, Testing 70%                │
└────────────────────────────────────────────────────────────────┘

 [R]efresh │ [N]ext Step │ [G]raph View │ [S]ettings │ [Q]uit
```

#### Interactive Features

**Navigation:**
```python
# Arrow keys to navigate sections
# Enter to drill down into details
# Tab to switch views (Progress, Graph, Learning Path, Stats)
```

**Live Updates:**
```python
# Auto-refresh every 5 seconds
# Show real-time updates as notes are created
# Animate progress bars and counters
```

**Drill-Down Views:**
```python
# Press 'G' for detailed graph view
# Press 'L' for full learning path
# Press 'A' for all achievements
# Press 'S' for detailed statistics
```

---

### 2. Web Dashboard (React + D3.js) 🌐

**Implementation:** FastAPI backend + React frontend

```
http://localhost:8080/onboarding/dashboard
```

**Features:**

#### Interactive Knowledge Graph Visualization
```javascript
// D3.js force-directed graph
<KnowledgeGraphVisualization
  nodes={notes}
  edges={relationships}
  interactive={true}
  highlight="current-learning-path"
/>
```

**Visual Elements:**
- **Nodes:** Notes sized by importance, colored by category
- **Edges:** Relationships with different line styles (builds_on, related_to, etc.)
- **Clusters:** Visual grouping of related concepts
- **Zoom/Pan:** Interactive exploration
- **Hover:** Show note previews
- **Click:** Open note details

#### Progress Dashboard
```jsx
<Dashboard>
  <ProgressRing completion={60} />
  <StatsGrid>
    <StatCard icon="📝" label="Notes" value="42/70" />
    <StatCard icon="🔗" label="Links" value="156" />
    <StatCard icon="📈" label="Score" value="847" />
  </StatsGrid>

  <LearningPathTimeline
    completed={["Python", "Git", "Testing"]}
    current="Async Programming"
    upcoming={["FastAPI", "API Testing"]}
  />

  <RecommendationsPanel>
    <NextStepCard priority="high" />
    <KnowledgeGapCard priority="medium" />
    <MarketplaceCard priority="low" />
  </RecommendationsPanel>
</Dashboard>
```

#### Achievements & Gamification
```jsx
<AchievementsGallery>
  <Achievement
    icon="🏆"
    title="First 10 Notes"
    earned={true}
    date="Oct 10, 2025"
  />
  <Achievement
    icon="🔗"
    title="Connector"
    earned={true}
    progress={56}
    requirement="50 links"
  />
  <Achievement
    icon="🌟"
    title="Domain Expert"
    earned={false}
    progress={80}
    requirement="Complete Python path"
  />
</AchievementsGallery>
```

#### Learning Velocity Chart
```jsx
<VelocityChart>
  {/* Line chart showing notes created over time */}
  {/* Bar chart showing knowledge coverage by category */}
  {/* Heatmap showing activity patterns */}
</VelocityChart>
```

---

### 3. Desktop Dashboard (Advanced Memory Pro) 🖥️

**Implementation:** Tauri + React in Advanced Memory Pro app

**Features:**

#### Native Desktop Experience
- **System tray integration:** Quick access to dashboard
- **Notifications:** Progress milestones and achievements
- **Offline support:** Full dashboard works offline
- **Native performance:** Fast rendering with Tauri

#### Sidebar Widget
```
┌─ Quick Stats ──────┐
│ 📊 Progress: 60%   │
│ 📝 Notes: 42       │
│ 🔥 Streak: 5 days  │
│                    │
│ [View Dashboard]   │
└────────────────────┘
```

#### Desktop-Specific Features
- **Keyboard shortcuts:** Global hotkeys for dashboard
- **Multi-window:** Dashboard in separate window
- **Screen recording:** Export knowledge graph as video
- **Export reports:** PDF/PNG of progress

---

### 4. MCP Tool Integration (Claude Desktop) 🤖

**Implementation:** New operations in `adn_zettelmaker`

```python
# View dashboard in Claude
adn_zettelmaker("dashboard", view="progress")

# Get recommendations
adn_zettelmaker("dashboard", view="recommendations")

# Check achievements
adn_zettelmaker("dashboard", view="achievements")

# View knowledge graph
adn_zettelmaker("dashboard", view="graph", format="ascii")
```

**Output Examples:**

#### Progress View
```
📊 Your Onboarding Progress

Overall: ████████████░░░░░░░░ 60% complete

Notes Created: 42 / 70 recommended
- ✅ Python Fundamentals (12 notes)
- ✅ Git Basics (8 notes)
- ✅ Testing (10 notes)
- 🔄 Async Programming (6/10 notes)
- 🔒 FastAPI (locked)

Knowledge Score: 847 / 1000
- Depth: 8.5/10
- Breadth: 7.2/10
- Connections: 9.1/10

Next milestone: 50 notes → Unlock "Knowledge Builder" achievement
```

#### ASCII Knowledge Graph
```
        Python ────┬──── FastAPI
          │        │       │
          │        └─── Async
          │              │
       Testing ────── Git
          │
        CI/CD ───── Docker

Clusters: 3 │ Orphans: 2 │ Depth: 3 levels
```

---

## Dashboard Data Model

### Onboarding Profile
```python
@dataclass
class OnboardingProfile:
    user_id: str
    started_at: datetime
    last_active: datetime

    # Progress metrics
    notes_created: int
    notes_recommended: int
    completion_percentage: float

    # Knowledge graph metrics
    total_connections: int
    cluster_count: int
    orphan_count: int
    average_depth: float

    # Learning path
    completed_topics: List[str]
    current_topic: str
    current_progress: float
    upcoming_topics: List[str]

    # Skill assessment
    detected_skill_level: str  # beginner, intermediate, advanced
    knowledge_coverage: Dict[str, float]  # category -> coverage %
    knowledge_gaps: List[str]

    # Engagement metrics
    days_active: int
    current_streak: int
    longest_streak: int
    notes_per_day: float

    # Achievements
    earned_achievements: List[Achievement]
    achievement_progress: Dict[str, float]

    # Recommendations
    next_steps: List[Recommendation]
    knowledge_score: int
```

### Achievement System
```python
@dataclass
class Achievement:
    id: str
    icon: str
    title: str
    description: str
    requirement: str
    earned: bool
    earned_at: Optional[datetime]
    progress: float  # 0.0 to 1.0

# Example achievements
ACHIEVEMENTS = [
    # Getting Started
    {"id": "first-note", "icon": "📝", "title": "First Note", "requirement": "Create 1 note"},
    {"id": "first-10", "icon": "🏆", "title": "Getting Started", "requirement": "Create 10 notes"},
    {"id": "first-50", "icon": "🎯", "title": "Knowledge Builder", "requirement": "Create 50 notes"},

    # Connections
    {"id": "first-link", "icon": "🔗", "title": "Connector", "requirement": "Create first wikilink"},
    {"id": "50-links", "icon": "🕸️", "title": "Web Weaver", "requirement": "Create 50 links"},
    {"id": "graph-master", "icon": "🌐", "title": "Graph Master", "requirement": "Create 200 links"},

    # Learning Paths
    {"id": "complete-path", "icon": "🎓", "title": "Graduate", "requirement": "Complete one learning path"},
    {"id": "polymath", "icon": "🧠", "title": "Polymath", "requirement": "Complete 3 learning paths"},

    # Speed
    {"id": "fast-learner", "icon": "⚡", "title": "Fast Learner", "requirement": "10 notes in one day"},
    {"id": "week-warrior", "icon": "🚀", "title": "Week Warrior", "requirement": "50 notes in one week"},

    # Streaks
    {"id": "streak-3", "icon": "🔥", "title": "On Fire", "requirement": "3 day streak"},
    {"id": "streak-7", "icon": "💪", "title": "Committed", "requirement": "7 day streak"},
    {"id": "streak-30", "icon": "🏅", "title": "Dedicated", "requirement": "30 day streak"},

    # Quality
    {"id": "deep-thinker", "icon": "🤔", "title": "Deep Thinker", "requirement": "Average note depth > 5"},
    {"id": "connector", "icon": "🌟", "title": "Master Connector", "requirement": "Avg 5 links per note"},

    # Community
    {"id": "marketplace", "icon": "🏪", "title": "Explorer", "requirement": "Install from marketplace"},
    {"id": "publisher", "icon": "📦", "title": "Publisher", "requirement": "Publish to marketplace"},
    {"id": "reviewer", "icon": "⭐", "title": "Reviewer", "requirement": "Rate 10 templates"},
]
```

### Recommendation Engine
```python
@dataclass
class Recommendation:
    type: str  # "next_step", "knowledge_gap", "marketplace", "connection"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    action: str  # Command or URL to execute
    reason: str

    # Context
    related_notes: List[str]
    estimated_time: str
    difficulty: str

# Example recommendations
{
    "type": "next_step",
    "priority": "high",
    "title": "Complete Async Programming",
    "description": "You're 60% through the Async module. Finish these 3 notes to unlock FastAPI.",
    "action": "adn_zettelmaker('generate', topic='async-python', remaining=True)",
    "reason": "You've shown strong progress in Python, and async is the next natural step",
    "estimated_time": "30 minutes",
    "difficulty": "intermediate"
}
```

---

## API Endpoints

### Dashboard API
```python
# Get dashboard data
GET /api/onboarding/dashboard
Response: OnboardingProfile

# Get progress details
GET /api/onboarding/progress
Response: {
    "completion": 0.6,
    "notes_created": 42,
    "notes_recommended": 70,
    "by_category": {...}
}

# Get knowledge graph data
GET /api/onboarding/graph
Response: {
    "nodes": [...],
    "edges": [...],
    "clusters": [...],
    "orphans": [...]
}

# Get recommendations
GET /api/onboarding/recommendations
Response: [Recommendation, ...]

# Get achievements
GET /api/onboarding/achievements
Response: [Achievement, ...]

# Update progress (internal)
POST /api/onboarding/progress
Body: {"action": "note_created", "note_id": "..."}
```

---

## Gamification Features

### Progress Tracking
- **Completion Percentage:** Overall onboarding progress
- **Category Coverage:** Percentage completion per category
- **Knowledge Score:** Weighted score based on depth, breadth, connections

### Streak System
```python
def calculate_streak(activity_dates: List[date]) -> int:
    """Calculate current streak of consecutive days."""
    # Count consecutive days with activity
    # Reset on gaps
    # Bonus points for streaks
```

### Level System
```python
LEVELS = [
    {"level": 1, "title": "Beginner", "requirement": 0},
    {"level": 2, "title": "Learner", "requirement": 100},
    {"level": 3, "title": "Explorer", "requirement": 300},
    {"level": 4, "title": "Builder", "requirement": 600},
    {"level": 5, "title": "Expert", "requirement": 1000},
    {"level": 6, "title": "Master", "requirement": 2000},
]
```

### Badges & Rewards
```python
# Unlock special features at milestones
REWARDS = {
    "first-50-notes": "Unlock advanced template customization",
    "complete-path": "Unlock AI-powered suggestions",
    "marketplace-publisher": "Unlock premium marketplace features",
    "knowledge-master": "Unlock expert-level templates",
}
```

---

## Implementation Plan

### Week 1-2: CLI Dashboard
- [x] Design terminal UI layout
- [ ] Implement Rich-based dashboard
- [ ] Add interactive navigation
- [ ] Create progress tracking
- [ ] Add achievement system

### Week 3: Web Dashboard Foundation
- [ ] Create FastAPI endpoints
- [ ] Design React components
- [ ] Implement D3.js graph visualization
- [ ] Add responsive layout

### Week 4: Web Dashboard Features
- [ ] Add progress charts
- [ ] Implement achievement gallery
- [ ] Create recommendation panel
- [ ] Add learning path timeline

### Week 5: Desktop Integration
- [ ] Integrate with Advanced Memory Pro
- [ ] Add native notifications
- [ ] Create sidebar widget
- [ ] Implement offline support

### Week 6: MCP Tool Integration
- [ ] Add dashboard operations to adn_zettelmaker
- [ ] Create ASCII graph rendering
- [ ] Format progress reports for Claude
- [ ] Add recommendation commands

### Week 7: Gamification
- [ ] Implement achievement tracking
- [ ] Add streak system
- [ ] Create level progression
- [ ] Design reward unlocks

### Week 8: Polish & Launch
- [ ] Performance optimization
- [ ] User testing
- [ ] Documentation
- [ ] Launch announcement

---

## Success Metrics

### Engagement
- **80%** of users check dashboard weekly
- **60%** complete recommended learning paths
- **50%** earn at least 5 achievements

### Effectiveness
- **40%** increase in note creation rate
- **3x** more connections created
- **2x** faster time to competency

### Satisfaction
- **4.5+** user rating for dashboard
- **90%** find recommendations helpful
- **85%** report feeling motivated by gamification

---

## Future Enhancements

### Social Features
- **Leaderboards:** Compare progress with friends
- **Challenges:** Weekly/monthly knowledge challenges
- **Sharing:** Share achievements on social media

### AI-Powered Insights
- **Personalized tips:** AI-generated learning advice
- **Pattern recognition:** Identify learning style patterns
- **Predictive analytics:** Suggest optimal study times

### Advanced Visualization
- **3D knowledge graph:** Interactive 3D visualization
- **Time-lapse:** Watch your knowledge graph grow
- **Heat maps:** Visualize activity patterns

### Integration
- **Calendar sync:** Track learning sessions
- **Goal tracking:** Set and monitor goals
- **Export reports:** Weekly/monthly progress reports

---

## Conclusion

The **Onboarding Dashboard** transforms zettelmaker from a content generator into a complete **learning experience platform**. By visualizing progress, gamifying achievements, and providing intelligent recommendations, we create an engaging, motivating environment that accelerates knowledge building.

**Cross-platform availability** (CLI, Web, Desktop, MCP) ensures users can track their progress anywhere, anytime.

**Next Step:** Implement CLI dashboard in Week 1-2 of Phase 4! 🚀

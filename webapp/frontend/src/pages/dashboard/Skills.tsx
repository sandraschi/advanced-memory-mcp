import {
  Bot,
  Calendar,
  Download,
  Plus,
  Save,
  Search,
  Share,
  Sparkles,
  Tag,
  Trash2,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

interface Skill {
  id: string;
  title: string;
  description: string;
  folder: string;
  tags: string[];
  created: string;
  modified: string;
  content: string;
  filePath: string;
  modules?: SkillModule[];
}

interface SkillModule {
  name: string;
  content: string;
}

interface SkillsProps {
  selectedSkillId?: string;
  onSkillSelect?: (skillId: string) => void;
}

export default function Skills({ selectedSkillId, onSkillSelect }: SkillsProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [filteredSkills, setFilteredSkills] = useState<Skill[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentFolder, setCurrentFolder] = useState("all");
  const [availableFolders, setAvailableFolders] = useState<string[]>([
    "all",
    "cursor-skills",
    "windsurf-skills",
    "adn-skills",
    "antigravity-skills",
  ]);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // No mock data — empty state shown when API unavailable

  const loadSkills = async () => {
    setIsLoading(true);
    try {
      const folderParam = currentFolder === "all" ? undefined : currentFolder;
      const response = await apiService.getSkills(folderParam);
      if (response.success && response.data?.skills) {
        const skillsData = response.data.skills;
        setSkills(skillsData);
        setFilteredSkills(skillsData);

        if (response.data.folders && response.data.folders.length > 0) {
          setAvailableFolders((prev) => {
            const fromApi = response.data!.folders as string[];
            if (prev[0] === "all") return ["all", ...fromApi];
            return fromApi;
          });
        }
        setIsLoading(false);
        return;
      }

      console.warn("Bridge server not available");
      setSkills([]);
      setFilteredSkills([]);
      setIsLoading(false);
    } catch (error) {
      console.error("Failed to load skills from API:", error);
      setSkills([]);
      setFilteredSkills([]);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSkills();
  }, [currentFolder]);

  useEffect(() => {
    // Filter skills based on search query
    if (searchQuery.trim() === "") {
      setFilteredSkills(skills);
    } else {
      const filtered = skills.filter(
        (skill) =>
          skill.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          skill.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
      );
      setFilteredSkills(filtered);
    }
  }, [searchQuery, skills]);

  useEffect(() => {
    // Select skill if selectedSkillId is provided
    if (selectedSkillId && skills.length > 0) {
      const skill = skills.find((s) => s.id === selectedSkillId);
      if (skill) {
        setSelectedSkill(skill);
      }
    }
  }, [selectedSkillId, skills]);

  const handleSkillSelect = (skill: Skill) => {
    setSelectedSkill(skill);
    onSkillSelect?.(skill.id);
  };

  const handleCreateSkill = () => {
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    setShowCreateModal(false);
  };

  return (
    <div className="flex h-full bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gold-400">Skills</h2>
            <button
              onClick={handleCreateSkill}
              className="p-2 bg-gold-600 hover:bg-gold-700 rounded-lg transition-colors"
              title="Create new skill"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          {/* Folder selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Skill Collection</label>
            <select
              value={currentFolder}
              onChange={(e) => setCurrentFolder(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            >
              {availableFolders.map((folder) => (
                <option key={folder} value={folder}>
                  {folder === "all"
                    ? "All collections"
                    : folder.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Skills List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-400">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-500 mx-auto mb-2"></div>
              Loading skills...
            </div>
          ) : filteredSkills.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <Bot className="w-12 h-12 mx-auto mb-2 text-gray-500" />
              {searchQuery ? "No skills match your search" : "No skills available. Create skills via MCP tools (adn_skills) or the skill creator."}
            </div>
          ) : (
            <div className="p-2">
              {filteredSkills.map((skill) => (
                <div
                  key={skill.id}
                  onClick={() => handleSkillSelect(skill)}
                  className={`p-3 mb-2 rounded-lg cursor-pointer transition-colors border ${
                    selectedSkill?.id === skill.id
                      ? "bg-gold-600 border-gold-500"
                      : "bg-gray-700 border-gray-600 hover:bg-gray-650"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white truncate">{skill.title}</h3>
                      <p className="text-sm text-gray-300 mt-1 line-clamp-2">{skill.description}</p>
                      {skill.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {skill.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                          {skill.tags.length > 3 && (
                            <span className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded-full">
                              +{skill.tags.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="ml-2 flex-shrink-0">
                      <Sparkles className="w-5 h-5 text-gold-400" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedSkill ? (
          <SkillViewer skill={selectedSkill} onClose={() => setSelectedSkill(null)} />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <Bot className="w-16 h-16 mx-auto mb-4 text-gray-500" />
              <h3 className="text-xl font-medium mb-2">Select a Skill</h3>
              <p>Choose a skill from the sidebar to view its details</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Skill Modal */}
      {showCreateModal && <CreateSkillModal onClose={handleCloseCreateModal} />}
    </div>
  );
}

// Skill Viewer Component
function SkillViewer({ skill, onClose }: { skill: Skill; onClose: () => void }) {
  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">{skill.title}</h1>
              <p className="text-gray-400 mt-1">{skill.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <Share className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center space-x-6 mt-4 text-sm text-gray-400">
          <div className="flex items-center space-x-1">
            <Tag className="w-4 h-4" />
            <span>{skill.folder}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>Created {new Date(skill.created).toLocaleDateString()}</span>
          </div>
          {skill.tags.length > 0 && (
            <div className="flex items-center space-x-2">
              {skill.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-700 text-gray-300 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="prose prose-invert max-w-none">
          <pre className="whitespace-pre-wrap text-gray-300 leading-relaxed">{skill.content}</pre>
        </div>

        {/* Modules */}
        {skill.modules && skill.modules.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-white mb-4">Modules</h2>
            <div className="space-y-4">
              {skill.modules.map((module, index) => (
                <div key={index} className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gold-400 mb-2">{module.name}</h3>
                  <pre className="whitespace-pre-wrap text-gray-300 text-sm">{module.content}</pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Create Skill Modal Component
function CreateSkillModal({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    folder: "cursor-skills",
    tags: "",
    overview: "",
    whenToUse: "",
  });
  const [modules, setModules] = useState<SkillModule[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedLLM, setSelectedLLM] = useState("");
  const [llmError, setLlmError] = useState("");

  const addModule = () => {
    setModules([...modules, { name: "", content: "" }]);
  };

  const removeModule = (index: number) => {
    setModules(modules.filter((_, i) => i !== index));
  };

  const updateModule = (index: number, field: keyof SkillModule, value: string) => {
    const updatedModules = [...modules];
    if (updatedModules[index]) {
      updatedModules[index][field] = value;
      setModules(updatedModules);
    }
  };

  const generateSkillContent = async () => {
    if (!formData.title || !selectedLLM) return;

    setIsGenerating(true);
    setLlmError("");

    try {
      // This would integrate with local LLM APIs (Ollama, LM Studio)
      // For now, generate basic content
      const generatedContent = `# ${formData.title}

${formData.overview || "This skill provides specialized guidance and automation for specific development tasks."}

## When to Use

${formData.whenToUse || "Apply this skill when working on related development tasks."}

## Key Features

- Specialized guidance for ${formData.title.toLowerCase()}
- Best practices and patterns
- Automation and tooling recommendations`;

      setFormData((prev) => ({ ...prev, overview: generatedContent }));
    } catch (error) {
      setLlmError("Failed to generate content with LLM");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async () => {
    // This would create the skill file and save it
    // For now, just close the modal
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create New Skill</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* LLM Generation Section */}
          <div className="mb-6 p-4 bg-gray-700 rounded-lg">
            <h3 className="text-lg font-medium text-white mb-3">Generate with AI</h3>
            <div className="flex space-x-4">
              <select
                value={selectedLLM}
                onChange={(e) => setSelectedLLM(e.target.value)}
                className="px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white focus:ring-2 focus:ring-gold-500"
              >
                <option value="">Select LLM</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="lmstudio">LM Studio (Local)</option>
              </select>
              <button
                onClick={generateSkillContent}
                disabled={isGenerating || !selectedLLM || !formData.title}
                className="px-4 py-2 bg-gold-600 hover:bg-gold-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center space-x-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isGenerating ? "Generating..." : "Generate Content"}</span>
              </button>
            </div>
            {llmError && <p className="text-red-400 text-sm mt-2">{llmError}</p>}
          </div>

          {/* Form Tabs */}
          <div className="mb-6">
            <div className="flex space-x-1">
              <button className="px-4 py-2 bg-gold-600 text-white rounded-lg">Overview</button>
              <button className="px-4 py-2 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-lg">
                Modules
              </button>
            </div>
          </div>

          {/* Overview Tab */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Skill title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Brief description"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Folder</label>
              <select
                value={formData.folder}
                onChange={(e) => setFormData((prev) => ({ ...prev, folder: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
              >
                <option value="cursor-skills">Cursor Skills</option>
                <option value="windsurf-skills">Windsurf Skills</option>
                <option value="adn-skills">ADN Skills</option>
                <option value="antigravity-skills">Antigravity Skills</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData((prev) => ({ ...prev, tags: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="tag1, tag2, tag3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Overview Content
              </label>
              <textarea
                value={formData.overview}
                onChange={(e) => setFormData((prev) => ({ ...prev, overview: e.target.value }))}
                rows={10}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent font-mono text-sm"
                placeholder="Skill content in markdown format"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">When to Use</label>
              <textarea
                value={formData.whenToUse}
                onChange={(e) => setFormData((prev) => ({ ...prev, whenToUse: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Describe when this skill should be applied"
              />
            </div>
          </div>

          {/* Modules Tab - Hidden for now */}
          <div className="hidden">
            <div className="space-y-4">
              {modules.map((module, index) => (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <input
                      type="text"
                      value={module.name}
                      onChange={(e) => updateModule(index, "name", e.target.value)}
                      placeholder="Module name"
                      className="flex-1 px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white mr-3"
                    />
                    <button
                      onClick={() => removeModule(index)}
                      className="p-2 text-red-400 hover:bg-red-900 rounded-lg"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <textarea
                    value={module.content}
                    onChange={(e) => updateModule(index, "content", e.target.value)}
                    rows={5}
                    placeholder="Module content"
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white font-mono text-sm"
                  />
                </div>
              ))}
              <button
                onClick={addModule}
                className="w-full py-2 border-2 border-dashed border-gray-600 rounded-lg text-gray-400 hover:border-gold-500 hover:text-gold-400 transition-colors flex items-center justify-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add Module</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-gold-600 hover:bg-gold-700 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Create Skill</span>
          </button>
        </div>
      </div>
    </div>
  );
}

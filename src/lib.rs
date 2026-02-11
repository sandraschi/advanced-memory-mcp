use zed_extension_api as zed;

struct AdvancedMemoryKnowledgeBaseExtension;

impl zed::Extension for AdvancedMemoryKnowledgeBaseExtension {
    fn new() -> Self {
        Self
    }

    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.as_ref() {
            "advanced-memory-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "advanced-memory-mcp".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.as_ref())),
        }
    }
}

zed::register_extension!(AdvancedMemoryKnowledgeBaseExtension);

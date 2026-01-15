use zed_extension_api as zed;

struct AdvancedMemoryKnowledgeBaseExtension;

impl zed::Extension for AdvancedMemoryKnowledgeBaseExtension {
    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.0.as_str() {
            "advanced-memory-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "advanced-memory-mcp".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.0)),
        }
    }
}

zed::register_extension!(AdvancedMemoryKnowledgeBaseExtension);

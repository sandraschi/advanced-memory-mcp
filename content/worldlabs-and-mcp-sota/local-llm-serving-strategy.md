# Local LLM Serving Strategy

**Timestamp**: 2026-01-23
**Status**: SOTA Active

- [architecture] Local **Ollama** instance masked as an OpenAI-compatible API.
- [networking] Uses **ngrok HTTPS tunnel** to expose port 11434 to Cursor's cloud servers for indexing and reasoning.
- [configuration] Set `OLLAMA_ORIGINS` to `*` to allow cross-origin requests from IDEs.
- [setup] Override OpenAI Base URL in Cursor settings to the ngrok URL + `/v1`.
- [cost] Zero API costs after hardware investment; only $20/month for the IDE pro account.

- relation_type [[RTX 4090 Inference Optimization]]
- relation_type [[Cursor IDE]]
- relation_type [[Windsurf IDE]]
- relation_type [[Antigravity IDE]]

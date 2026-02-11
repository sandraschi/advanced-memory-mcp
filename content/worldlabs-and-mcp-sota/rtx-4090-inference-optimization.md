# RTX 4090 Inference Optimization

**Timestamp**: 2026-01-23
**Status**: SOTA Standard

- [buffer] **Last Byte Rule**: Never load VRAM past 22GB (out of 24GB).
- [kv_cache] Requires ~2GB buffer for the KV Cache to grow; saturation causes 90% performance drop due to DDR5 swapping.
- [models] **Qwen2.5-Coder-32B** is the "Daily Driver" champion for 24GB cards.
- [reasoning] **DeepSeek-R1-Distill-Qwen-32B** for complex debugging using Chain-of-Thought.
- [modelfile] Custom Ollama Modelfile used to lock in `num_ctx 32768`, `num_gpu 99`, and `keep_alive 24h`.
- [rag] Full-Project RAG in IDEs requires larger context windows (32k+) to fit retrieved code snippets.

- relation_type [[Local LLM Serving Strategy]]
- relation_type [[Qwen2.5-Coder-32B]]
- relation_type [[DeepSeek-R1]]

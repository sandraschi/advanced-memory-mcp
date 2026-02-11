# WorldLabs AI Integration

**Timestamp**: 2026-01-23
**Status**: Integrated

- [architecture] Integrated into MyHomeServer backend via `WorldLabsClient` in `app.services.worldlabs`.
- [api] Uses `platform.worldlabs.ai` for generating 3D worlds (marbles) from text, images, or video.
- [frontend] Dedicated "WorldLabs 3D" page in the React dashboard for triggering generation and viewing interactive results.
- [config] Requires `WORLDLABS_API_KEY` in `.env` file.
- [workflow] Asynchronous generation with status polling implemented in the frontend.

- relation_type [[MyHomeServer]]
- relation_type [[FastAPI]]
- relation_type [[React Dashboard]]

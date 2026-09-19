"""Entry: python -m advanced_memory."""

import os

import uvicorn

from advanced_memory.api.app import app


def main():
    port = int(os.getenv("PORT", "10705"))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

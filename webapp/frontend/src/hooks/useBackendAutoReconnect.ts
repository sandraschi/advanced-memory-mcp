import { useEffect, useRef } from "react";

import { getApiBaseUrl } from "../config/apiBase";

const DEFAULT_INTERVAL_MS = 12_000;
const HEALTH_MS = 10_000;

/**
 * Polls /health while `enabled`. When the API is back, runs `onRecovered` once per interval tick.
 * Browsers cannot spawn uvicorn; this only detects when you have restarted the process yourself.
 */
export function useBackendAutoReconnect(
  enabled: boolean,
  onRecovered: () => void | Promise<void>,
  intervalMs = DEFAULT_INTERVAL_MS,
): void {
  const cbRef = useRef(onRecovered);
  cbRef.current = onRecovered;

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const tick = () => {
      void (async () => {
        try {
          const r = await fetch(`${getApiBaseUrl()}/health`, {
            method: "GET",
            signal: AbortSignal.timeout(HEALTH_MS),
          });
          if (!r.ok) {
            return;
          }
          await cbRef.current();
        } catch {
          /* still unreachable */
        }
      })();
    };
    const id = window.setInterval(tick, intervalMs);
    void tick();
    return () => window.clearInterval(id);
  }, [enabled, intervalMs]);
}

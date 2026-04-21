/** Dev-only logging — keeps production consoles clean. */

const dev = import.meta.env.DEV;

export function devError(...args: unknown[]): void {
  if (!dev) {
    return;
  }
  // biome-ignore lint/suspicious/noConsoleLog: intentional dev-only sink
  console.error(...args);
}

export function devWarn(...args: unknown[]): void {
  if (!dev) {
    return;
  }
  // biome-ignore lint/suspicious/noConsoleLog: intentional dev-only sink
  console.warn(...args);
}

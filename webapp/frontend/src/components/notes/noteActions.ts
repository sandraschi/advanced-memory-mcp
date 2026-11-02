import { apiService } from "../../services/api";
import { emitVault } from "./noteUtils";

/** Clipboard write that never throws; resolves false when the browser refuses. */
export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/** Absolute URL that reopens a note in the vault (read by NoteViewer's ?id= handling). */
export function noteDeepLink(id: string): string {
  return `${window.location.origin}/notes?id=${encodeURIComponent(id)}`;
}

/**
 * Ask for confirmation, delete through the API, then tell the rest of the app.
 * `deleted` is false both when the user cancels (no error) and when the API fails (error set).
 */
export async function confirmAndDeleteNote(
  id: string,
  title: string,
): Promise<{ deleted: boolean; error?: string }> {
  if (
    !window.confirm(`Delete "${title}"?\n\nThis removes the note and its search index entries.`)
  ) {
    return { deleted: false };
  }
  const res = await apiService.deleteNote(id);
  if (!res.success) {
    return { deleted: false, error: res.error || "Delete failed" };
  }
  emitVault({ type: "deleted", id });
  return { deleted: true };
}

import type { LogInfo } from "./types";

export const ACCENTS = ["violet", "cyan", "blue", "orange", "rose", "teal"] as const;
export type Accent = (typeof ACCENTS)[number];

export const plural = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;

export function timeAgo(iso: string | null, now = Date.now()): string {
  if (!iso) return "";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const minutes = Math.round((now - then) / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return plural(hours, "hour") + " ago";
  const days = Math.round(hours / 24);
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  return new Date(then).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

/** '/home/sam/Downloads' -> '~/Downloads' when the home folder is known. */
export function shortPath(path: string, home?: string): string {
  if (home && (path === home || path.startsWith(home + "/") || path.startsWith(home + "\\"))) {
    return "~" + path.slice(home.length);
  }
  return path;
}

const SEPARATOR = /[\\/]/;

export const baseName = (path: string) => path.split(SEPARATOR).filter(Boolean).pop() ?? path;

export function dirName(path: string): string {
  const cut = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"));
  return cut <= 0 ? "" : path.slice(0, cut);
}

export function relative(path: string, folder: string): string {
  const base = folder.replace(/[\\/]+$/, "");
  return path.startsWith(base) ? path.slice(base.length).replace(/^[\\/]+/, "") : path;
}

export function extension(filename: string): string {
  const dot = filename.lastIndexOf(".");
  return dot > 0 && dot < filename.length - 1 ? filename.slice(dot + 1).toLowerCase() : "";
}

/** The same extension always gets the same color. */
export function extAccent(ext: string): Accent {
  let hash = 0;
  for (const char of ext) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return ACCENTS[hash % ACCENTS.length];
}

/** Colour for a group like 'docs_pdf/' or 'delete .tmp' so bars match the file badges below them. */
export function groupAccent(name: string): Accent {
  const token = name.replace(/\/$/, "").split(/[_\s]/).pop() ?? name;
  return extAccent(token.replace(/^\./, "").toLowerCase());
}

export type RunKind = "organize" | "move" | "delete" | "remove" | "undo";

export function runKind(run: Pick<LogInfo, "operation" | "kind">): RunKind {
  if (run.kind === "undo") return "undo";
  if (run.operation.startsWith("organize")) return "organize";
  if (run.operation.startsWith("move")) return "move";
  if (run.operation === "clean_empty_folders") return "remove";
  return "delete";
}

export const VERB: Record<RunKind, string> = {
  organize: "organized",
  move: "moved",
  delete: "deleted",
  remove: "removed",
  undo: "restored",
};

export type RunStatus = { label: string; tone: "ok" | "muted" | "warn" | "bad" };

export function runStatus(run: LogInfo): RunStatus {
  if (run.kind === "undo") return { label: "Restored", tone: "ok" };
  if (run.undone) return { label: "Undone", tone: "muted" };
  if (run.status === "interrupted") return { label: "Interrupted", tone: "warn" };
  if (run.summary.failed > 0) {
    return run.summary.done > 0 ? { label: "Partial", tone: "warn" } : { label: "Failed", tone: "bad" };
  }
  return { label: "Done", tone: "ok" };
}

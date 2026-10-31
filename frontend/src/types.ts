export type OptionSpec = {
  name: string;
  label: string;
  type: "bool" | "text" | "extension" | "folder";
  default?: boolean;
  required?: boolean;
};

export type Operation = {
  id: string;
  name: string;
  description: string;
  options: OptionSpec[];
};

export type Action = {
  id?: number;
  op: string;
  src: string;
  dest?: string;
  status?: string;
  final_dest?: string;
  trashed_to?: string;
  error?: string;
};

export type Plan = {
  plan_id: string;
  operation: string;
  folder: string;
  options: Record<string, unknown>;
  actions: (Action & { id: number })[];
  groups: { name: string; count: number }[];
  dangerous: boolean;
};

export type Summary = { done: number; skipped: number; failed: number; pending: number };

export type LogInfo = {
  id: string;
  kind: "run" | "undo";
  operation: string;
  folder: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  summary: Summary;
  undone: boolean;
  undo_of?: string;
};

export type Log = LogInfo & { actions: Action[] };

export type BrowseResult = {
  path: string;
  parent: string | null;
  folders: string[];
  blocked: string | null;
};

export type ExtensionCount = { extension: string; count: number };

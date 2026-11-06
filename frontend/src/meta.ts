import type { Accent } from "./format";
import type { IconName } from "./icons";

export type Category = "Organize" | "Move" | "Clean";

export type OperationMeta = {
  icon: IconName;
  accent: Accent;
  category: Category;
  blurb: string; // short line on the home card
  lead: string; // line under the title on the setup page
};

export const META: Record<string, OperationMeta> = {
  organize_by_extension: {
    icon: "layers",
    accent: "violet",
    category: "Organize",
    blurb: "Sort files into folders like docs_pdf, docs_jpg.",
    lead: "Pick a folder and choose how to group its files.",
  },
  organize_by_date: {
    icon: "calendar",
    accent: "cyan",
    category: "Organize",
    blurb: "One folder per day, based on when files changed.",
    lead: "Pick a folder. Each file goes into a folder named after the day it last changed.",
  },
  move_by_extension: {
    icon: "move",
    accent: "blue",
    category: "Move",
    blurb: "Send every .jpg (or any type) to another folder.",
    lead: "Choose a file type and where those files should go.",
  },
  clean_by_extension: {
    icon: "trash",
    accent: "orange",
    category: "Clean",
    blurb: "Remove all files of one type. Goes to trash.",
    lead: "Choose a file type to remove. You can review everything before it happens.",
  },
  clean_by_name: {
    icon: "fileX",
    accent: "rose",
    category: "Clean",
    blurb: "Remove files whose name contains some text.",
    lead: "Type part of a file name. Every file containing it will be listed for review.",
  },
  clean_empty_folders: {
    icon: "folderMinus",
    accent: "teal",
    category: "Clean",
    blurb: "Tidy up folders that hold nothing.",
    lead: "Pick a folder. Folders with no files inside are listed for review.",
  },
};

export const FALLBACK_META: OperationMeta = {
  icon: "sparkle",
  accent: "violet",
  category: "Clean",
  blurb: "",
  lead: "",
};

export const metaFor = (id: string): OperationMeta => META[id] ?? FALLBACK_META;

// ---- "What will happen" examples shown beside the setup form ----

export type ExampleRow = { kind: "file" | "folder"; name: string; level?: 0 | 1; faded?: boolean };
export type Example = { before: ExampleRow[]; after: ExampleRow[] };

const file = (name: string, level: 0 | 1 = 0, faded = false): ExampleRow => ({ kind: "file", name, level, faded });
const folder = (name: string, level: 0 | 1 = 0, faded = false): ExampleRow => ({ kind: "folder", name, level, faded });

export function example(operation: string, values: Record<string, unknown>): Example {
  const text = (name: string, fallback: string) => String(values[name] ?? "").trim() || fallback;
  const ext = (fallback: string) => (typeof values.extension === "string" && values.extension ? values.extension : fallback);

  switch (operation) {
    case "organize_by_extension": {
      const label = text("label", "docs").toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "") || "docs";
      return {
        before: [file("report.pdf"), file("invoice.pdf"), file("photo.jpg"), file("notes.txt")],
        after: [
          folder(`${label}_pdf`), file("report.pdf", 1), file("invoice.pdf", 1),
          folder(`${label}_jpg`), file("photo.jpg", 1),
          folder(`${label}_txt`), file("notes.txt", 1),
        ],
      };
    }
    case "organize_by_date":
      return {
        before: [file("standup.txt"), file("budget.xlsx"), file("photo.jpg")],
        after: [folder("2025-03-04"), file("standup.txt", 1), file("photo.jpg", 1), folder("2025-03-05"), file("budget.xlsx", 1)],
      };
    case "move_by_extension": {
      const e = ext(".jpg");
      return {
        before: [file(`sunset${e}`), file(`beach${e}`), file("notes.txt")],
        after: [folder("Target folder"), file(`sunset${e}`, 1), file(`beach${e}`, 1), file("notes.txt", 0, true)],
      };
    }
    case "clean_by_extension": {
      const e = ext(".tmp");
      return {
        before: [file(`cache${e}`), file(`old${e}`), file("report.pdf")],
        after: [folder("Sortify trash"), file(`cache${e}`, 1), file(`old${e}`, 1), file("report.pdf", 0, true)],
      };
    }
    case "clean_by_name": {
      const t = text("name", "draft");
      return {
        before: [file(`${t}-1.txt`), file(`final-${t}.doc`), file("notes.txt")],
        after: [folder("Sortify trash"), file(`${t}-1.txt`, 1), file(`final-${t}.doc`, 1), file("notes.txt", 0, true)],
      };
    }
    default:
      return {
        before: [folder("empty-1"), folder("old-photos"), folder("keep"), file("a.txt", 1)],
        after: [folder("keep"), file("a.txt", 1)],
      };
  }
}

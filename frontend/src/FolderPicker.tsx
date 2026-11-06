import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { Icon, type IconName } from "./icons";
import type { BrowseResult } from "./types";
import { Switch } from "./ui";

type Props = { start: string; title?: string; onPick: (path: string) => void; onClose: () => void };

const PLACE_ICONS: Record<string, IconName> = {
  Home: "home",
  Desktop: "monitor",
  Downloads: "download",
  Documents: "documents",
  Pictures: "image",
};

/** 'C:\Users\sam' -> [{name:'C:', path:'C:\'}, ...]; '/Users/sam' -> [{name:'/', path:'/'}, ...] */
export function breadcrumbs(path: string): { name: string; path: string }[] {
  const windows = /^[A-Za-z]:/.test(path) || (path.includes("\\") && !path.includes("/"));
  const parts = path.split(/[\\/]+/).filter(Boolean);
  const crumbs = windows ? [] : [{ name: "/", path: "/" }];
  parts.forEach((name, i) => {
    const joined = parts.slice(0, i + 1).join(windows ? "\\" : "/");
    crumbs.push({ name, path: windows ? (i === 0 ? joined + "\\" : joined) : "/" + joined });
  });
  return crumbs;
}

export default function FolderPicker({ start, title = "Choose a folder", onPick, onClose }: Props) {
  const [data, setData] = useState<BrowseResult | null>(null);
  const [hidden, setHidden] = useState(false);
  const [error, setError] = useState("");
  const dialog = useRef<HTMLDivElement>(null);

  const open = (path: string, showHidden = hidden) =>
    api
      .browse(path, showHidden)
      .then((result) => {
        setData(result);
        setError("");
      })
      .catch((e: Error) => setError(e.message));

  useEffect(() => {
    open(start);
    dialog.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const child = (name: string) => {
    if (!data) return name;
    const sep = data.path.includes("\\") && !data.path.includes("/") ? "\\" : "/";
    return data.path.replace(/[\\/]+$/, "") + sep + name;
  };

  const current = data ? data.path.split(/[\\/]+/).filter(Boolean).pop() || data.path : "";

  return (
    <div className="overlay" onClick={onClose}>
      <div className="dialog" role="dialog" aria-modal="true" aria-label={title} tabIndex={-1} ref={dialog}
        onClick={(e) => e.stopPropagation()}>
        <div className="dialog-head">
          <h2>{title}</h2>
          <button className="btn icon-only" onClick={onClose} aria-label="Close">
            <Icon name="x" size={18} />
          </button>
        </div>

        <div className="chips">
          {data?.shortcuts.map((place) => (
            <button key={place.path} className={`chip ${data.path === place.path ? "sel" : ""}`} onClick={() => open(place.path)}>
              <Icon name={PLACE_ICONS[place.name] ?? "folder"} size={16} /> {place.name}
            </button>
          ))}
        </div>

        <nav className="crumbs" aria-label="Current location">
          {data && breadcrumbs(data.path).map((crumb, i, all) => (
            <span key={crumb.path} className="crumb-wrap">
              {i > 0 && <Icon name="chevronRight" size={14} />}
              <button className={`crumb ${i === all.length - 1 ? "now" : ""}`} onClick={() => open(crumb.path)}>
                {crumb.name}
              </button>
            </span>
          ))}
        </nav>

        <div className="folder-list" role="list">
          {data?.parent && (
            <button className="frow-pick up" onClick={() => open(data.parent!)}>
              <Icon name="chevronUp" size={18} />
              <span>Parent folder</span>
            </button>
          )}
          {data?.folders.map((folder) => (
            <button key={folder.name} className="frow-pick" onClick={() => open(child(folder.name))}>
              <Icon name="folder" size={20} />
              <span className="fname">{folder.name}</span>
              {folder.items !== null && (
                <span className="muted">{folder.items} {folder.items === 1 ? "item" : "items"}</span>
              )}
              <Icon name="chevronRight" size={16} />
            </button>
          ))}
          {data && data.folders.length === 0 && <p className="muted pad">No subfolders here.</p>}
          {!data && !error && <p className="muted pad">Loading…</p>}
        </div>

        {error && <p className="note bad"><Icon name="alert" size={18} /> {error}</p>}
        {data?.blocked && <p className="note bad"><Icon name="alert" size={18} /> This folder can't be used: {data.blocked}.</p>}

        <Switch checked={hidden} onChange={(value) => { setHidden(value); open(data?.path ?? start, value); }}>
          Show hidden folders
        </Switch>

        <div className="row end">
          <button className="btn" onClick={onClose}>Cancel</button>
          <button className="btn primary" disabled={!data || !!data.blocked} onClick={() => data && onPick(data.path)}>
            Use “{current}”
          </button>
        </div>
      </div>
    </div>
  );
}

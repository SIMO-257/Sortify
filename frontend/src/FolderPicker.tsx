import { useEffect, useState } from "react";
import { api } from "./api";
import type { BrowseResult } from "./types";

type Props = { start: string; onPick: (path: string) => void; onClose: () => void };

export default function FolderPicker({ start, onPick, onClose }: Props) {
  const [data, setData] = useState<BrowseResult | null>(null);
  const [hidden, setHidden] = useState(false);
  const [error, setError] = useState("");

  const open = (path: string) =>
    api
      .browse(path, hidden)
      .then((result) => {
        setData(result);
        setError("");
      })
      .catch((e: Error) => setError(e.message));

  useEffect(() => {
    open(data?.path ?? start);
  }, [hidden]);

  const join = (name: string) => (data ? data.path.replace(/[\\/]$/, "") + (data.path.includes("\\") ? "\\" : "/") + name : name);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="dialog" role="dialog" aria-label="Choose a folder" onClick={(e) => e.stopPropagation()}>
        <h2>Choose a folder</h2>
        <p className="path">{data?.path ?? "…"}</p>
        {error && <p className="error">{error}</p>}
        <ul className="folders">
          {data?.parent && (
            <li>
              <button className="link" onClick={() => open(data.parent!)}>
                ⬆ ..
              </button>
            </li>
          )}
          {data?.folders.map((name) => (
            <li key={name}>
              <button className="link" onClick={() => open(join(name))}>
                📁 {name}
              </button>
            </li>
          ))}
          {data && data.folders.length === 0 && <li className="muted">No subfolders</li>}
        </ul>
        {data?.blocked && <p className="error">Cannot be used: {data.blocked}.</p>}
        <label className="check">
          <input type="checkbox" checked={hidden} onChange={(e) => setHidden(e.target.checked)} /> Show hidden folders
        </label>
        <div className="row end">
          <button onClick={onClose}>Cancel</button>
          <button className="primary" disabled={!data || !!data.blocked} onClick={() => data && onPick(data.path)}>
            Use this folder
          </button>
        </div>
      </div>
    </div>
  );
}

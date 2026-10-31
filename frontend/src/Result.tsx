import { useState } from "react";
import { api } from "./api";
import type { Log } from "./types";

type Props = { log: Log; onUndone: (log: Log) => void; onClose: () => void; closeLabel: string };

export default function Result({ log, onUndone, onClose, closeLabel }: Props) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const failed = log.actions.filter((a) => a.status === "failed");
  const canUndo = log.kind === "run" && !log.undone && log.summary.done > 0;
  const verb = log.kind === "undo" ? "Restored" : "Done";

  const undo = async () => {
    setBusy(true);
    setError("");
    try {
      onUndone(await api.undo(log.id));
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  };

  return (
    <div className="card stack">
      <h2>{log.kind === "undo" ? "Undo finished" : "Finished"}</h2>
      <p className="muted">
        {log.operation} · {log.folder} · {log.started_at}
      </p>
      <ul className="stats">
        <li>
          <strong>{log.summary.done}</strong> {verb.toLowerCase()}
        </li>
        <li>
          <strong>{log.summary.skipped}</strong> skipped
        </li>
        <li className={failed.length ? "error" : ""}>
          <strong>{log.summary.failed}</strong> failed
        </li>
      </ul>
      {log.undone && <p className="muted">This run was undone.</p>}

      {failed.length > 0 && (
        <ul className="files">
          {failed.map((a, i) => (
            <li key={i} className="error">
              {a.src}: {a.error}
            </li>
          ))}
        </ul>
      )}

      {error && <p className="error">{error}</p>}
      <div className="row end">
        <button onClick={onClose}>{closeLabel}</button>
        {canUndo && (
          <button className="primary" onClick={undo} disabled={busy}>
            {busy ? "Undoing…" : "Undo this run"}
          </button>
        )}
      </div>
    </div>
  );
}

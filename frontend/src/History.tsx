import { useEffect, useState } from "react";
import { api } from "./api";
import type { LogInfo } from "./types";

type Props = { onOpen: (id: string) => void; onBack: () => void };

export default function History({ onOpen, onBack }: Props) {
  const [runs, setRuns] = useState<LogInfo[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.logs().then(setRuns).catch((e: Error) => setError(e.message));
  }, []);

  return (
    <div className="card stack">
      <h2>History</h2>
      {error && <p className="error">{error}</p>}
      {runs && runs.length === 0 && <p className="muted">No runs yet.</p>}
      <ul className="runs">
        {runs?.map((run) => (
          <li key={run.id}>
            <button className="link" onClick={() => onOpen(run.id)}>
              <strong>{run.kind === "undo" ? "↩ Undo of " : ""}{run.operation}</strong>
              <span className="muted">
                {" "}
                {run.started_at} · {run.folder}
              </span>
              <span className="muted">
                {" "}
                · {run.summary.done} done, {run.summary.failed} failed{run.undone ? " · undone" : ""}
                {run.status === "interrupted" ? " · interrupted" : ""}
              </span>
            </button>
          </li>
        ))}
      </ul>
      <div className="row end">
        <button onClick={onBack}>Back</button>
      </div>
    </div>
  );
}

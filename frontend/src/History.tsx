import { useEffect, useState } from "react";
import { api } from "./api";
import { runKind, runStatus, shortPath, timeAgo, VERB } from "./format";
import { Icon } from "./icons";
import { metaFor } from "./meta";
import type { LogInfo, Operation } from "./types";
import { IconTile } from "./ui";

type Props = { operations: Operation[] | null; home?: string; onOpen: (id: string) => void; onError: (text: string) => void };

export default function History({ operations, home, onOpen, onError }: Props) {
  const [runs, setRuns] = useState<LogInfo[] | null>(null);

  useEffect(() => {
    api.logs().then(setRuns).catch((e: Error) => { setRuns([]); onError(e.message); });
  }, []);

  const names = Object.fromEntries((operations ?? []).map((o) => [o.id, o.name]));

  return (
    <div className="view">
      <h1 className="hero sm">History</h1>
      <p className="lead">Every run is saved on your computer. Open one to see each file, or undo it.</p>

      {runs === null && Array.from({ length: 4 }, (_, i) => <div key={i} className="rrow skeleton" aria-hidden="true" />)}
      {runs?.length === 0 && (
        <div className="empty big">
          <Icon name="clock" size={30} />
          <b>No runs yet</b>
          <span>When you organize, move or clean files, each run will be listed here.</span>
        </div>
      )}

      <div className="runs">
        {runs?.map((run) => {
          const meta = metaFor(run.operation);
          const status = runStatus(run);
          const title = (names[run.operation] ?? run.operation) + (run.kind === "undo" ? " (undo)" : "");
          return (
            <button key={run.id} className="rrow" onClick={() => onOpen(run.id)}>
              <IconTile name={run.kind === "undo" ? "undo" : meta.icon} accent={run.kind === "undo" ? "blue" : meta.accent} size="sm" />
              <span className="rtxt">
                <b>{title}</b>
                <span className="mono">{shortPath(run.folder, home)}</span>
              </span>
              <span className="muted col-count">
                {run.summary.done} {VERB[runKind(run)]}{run.summary.failed ? ` · ${run.summary.failed} failed` : ""}
              </span>
              <span className="muted col-time" title={run.started_at}>{timeAgo(run.started_at)}</span>
              <span className={`badge ${status.tone}`}>{status.label}</span>
              <span className="go flat" aria-hidden="true"><Icon name="chevronRight" size={16} /></span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

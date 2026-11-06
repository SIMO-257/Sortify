import { useEffect, useState } from "react";
import { api } from "./api";
import { runKind, runStatus, shortPath, timeAgo, VERB } from "./format";
import { Icon } from "./icons";
import { metaFor } from "./meta";
import type { LogInfo, Operation } from "./types";
import { IconTile, type Notify } from "./ui";

type Props = {
  operations: Operation[] | null;
  home?: string;
  onPick: (operation: Operation) => void;
  onOpenRun: (id: string) => void;
  notify: Notify;
};

const BADGES = [
  { icon: "lock", text: "100% local" },
  { icon: "eye", text: "Preview before changes" },
  { icon: "undo", text: "Undo any run" },
] as const;

export default function Home({ operations, home, onPick, onOpenRun, notify }: Props) {
  const [runs, setRuns] = useState<LogInfo[] | null>(null);
  const [undoing, setUndoing] = useState("");

  const loadRuns = () =>
    api.logs().then((all) => setRuns(all.filter((r) => r.kind === "run").slice(0, 3))).catch(() => setRuns([]));

  useEffect(() => {
    loadRuns();
  }, []);

  const names = Object.fromEntries((operations ?? []).map((o) => [o.id, o.name]));

  const undo = async (run: LogInfo) => {
    setUndoing(run.id);
    try {
      const result = await api.undo(run.id);
      notify(`Restored ${result.summary.done} ${result.summary.done === 1 ? "item" : "items"}.`, "success");
      await loadRuns();
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setUndoing("");
    }
  };

  return (
    <div className="view">
      <h1 className="hero">
        Tidy your files in <span className="grad">seconds</span>.
      </h1>
      <p className="lead">Sort, move and clean folders on your own computer. See exactly what will happen before anything changes.</p>
      <div className="badges">
        {BADGES.map((b) => (
          <span className="bdg" key={b.text}>
            <Icon name={b.icon} size={17} /> {b.text}
          </span>
        ))}
      </div>

      <div className="grid">
        {operations === null
          ? Array.from({ length: 6 }, (_, i) => <div key={i} className="card op skeleton" aria-hidden="true" />)
          : operations.map((operation) => {
              const meta = metaFor(operation.id);
              return (
                <button key={operation.id} className="card op" onClick={() => onPick(operation)}>
                  <span className="optop">
                    <IconTile name={meta.icon} accent={meta.accent} size="lg" />
                    <span className="pill">{meta.category}</span>
                  </span>
                  <h3>{operation.name}</h3>
                  <p>{meta.blurb || operation.description}</p>
                  <span className="go" aria-hidden="true">
                    <Icon name="arrowRight" size={18} />
                  </span>
                </button>
              );
            })}
      </div>

      <h2 className="sec">Recent activity</h2>
      {runs !== null && runs.length === 0 && (
        <div className="empty">
          <Icon name="sparkle" size={26} />
          <span>Nothing yet. Pick an operation above and your first run will show up here.</span>
        </div>
      )}
      <div className="runs">
        {runs?.map((run) => {
          const meta = metaFor(run.operation);
          const status = runStatus(run);
          const canUndo = !run.undone && run.summary.done > 0;
          return (
            <div key={run.id} className="rrow" role="button" tabIndex={0} onClick={() => onOpenRun(run.id)}
              onKeyDown={(e) => e.key === "Enter" && onOpenRun(run.id)}>
              <IconTile name={meta.icon} accent={meta.accent} size="sm" />
              <span className="rtxt">
                <b>{names[run.operation] ?? run.operation}</b>
                <span className="mono">{shortPath(run.folder, home)}</span>
              </span>
              <span className="muted col-count">{run.summary.done} {VERB[runKind(run)]}</span>
              <span className="muted col-time">{timeAgo(run.started_at)}</span>
              {canUndo ? (
                <button className="mini" disabled={undoing === run.id}
                  onClick={(e) => { e.stopPropagation(); undo(run); }}>
                  <Icon name="undo" size={15} /> {undoing === run.id ? "Undoing…" : "Undo"}
                </button>
              ) : (
                <span className={`badge ${status.tone}`}>{status.label}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

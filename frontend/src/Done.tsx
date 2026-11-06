import { useState } from "react";
import { api } from "./api";
import { baseName, plural, runKind, runStatus, shortPath, timeAgo, VERB } from "./format";
import { Icon } from "./icons";
import { metaFor } from "./meta";
import type { Action, Log } from "./types";
import { IconTile, Stat, type Notify } from "./ui";

type Props = {
  log: Log;
  operationName: string;
  home?: string;
  detail?: boolean; // opened from History: show the file list and a different headline
  closeLabel: string;
  onClose: () => void;
  onUndone: (log: Log) => void;
  notify: Notify;
};

const PAGE = 100;

export default function Done({ log, operationName, home, detail, closeLabel, onClose, onUndone, notify }: Props) {
  const [busy, setBusy] = useState(false);
  const [shown, setShown] = useState(PAGE);
  const kind = runKind(log);
  const status = runStatus(log);
  const meta = metaFor(log.operation);
  const failed = log.actions.filter((a) => a.status === "failed");
  const { done, skipped } = log.summary;
  const problems = log.summary.failed;
  const nothing = done === 0 && problems > 0;
  const canUndo = log.kind === "run" && !log.undone && done > 0;
  const unit = kind === "remove" ? "folder" : "file";

  const undo = async () => {
    setBusy(true);
    try {
      onUndone(await api.undo(log.id));
    } catch (e) {
      notify((e as Error).message);
      setBusy(false);
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(log.folder);
      notify("Folder path copied.", "success");
    } catch {
      notify("Could not copy. Select the path and copy it by hand.");
    }
  };

  const verb = VERB[kind];
  const headline = nothing ? (
    <>Nothing could be <span className="grad bad">changed</span></>
  ) : detail ? (
    <>{operationName}</>
  ) : (
    <>{plural(done, unit)} <span className="grad">{verb}</span></>
  );

  const icon = nothing ? "alert" : "check";
  const label = (a: Action) => (a.status === "failed" ? "alert" : a.status === "skipped" ? "clock" : "check");

  return (
    <div className="view">
      <section className="card pad-xl center">
        <div className={`ring ${nothing ? "bad" : problems ? "warn" : ""}`}><Icon name={icon} size={52} strokeWidth={3} /></div>
        <h1 className="hero sm">{headline}</h1>
        {detail && (
          <p className="lead tight">
            <span className={`badge ${status.tone}`}>{status.label}</span> {timeAgo(log.started_at)} · {plural(done, unit)} {verb}
          </p>
        )}
        <p className="lead tight">
          {log.kind === "undo" ? "Put back in" : detail ? "In" : "Everything is in place in"}{" "}
          <button className="pathcopy mono" onClick={copy} title="Copy the folder path">
            {shortPath(log.folder, home)} <Icon name="copy" size={15} />
          </button>
        </p>

        <div className="tiles narrow">
          <Stat value={done} label={verb} tone={done ? "ok" : undefined} />
          <Stat value={skipped} label="skipped" />
          <Stat value={problems} label="failed" tone={problems ? "bad" : undefined} />
          {kind === "organize" && <Stat value={log.created_dirs?.length ?? 0} label="new folders" />}
          {kind === "delete" && <Stat value={done} label="in the trash" />}
        </div>

        {log.undone && <p className="note info"><Icon name="undo" size={18} /> This run was undone. Everything was put back.</p>}

        <div className="row center-row">
          <button className="btn" onClick={onClose}>{closeLabel}</button>
          {canUndo && (
            <button className="btn primary" onClick={undo} disabled={busy}>
              <Icon name="undo" size={17} /> {busy ? "Undoing…" : "Undo this run"}
            </button>
          )}
        </div>
      </section>

      {failed.length > 0 && (
        <section className="card pad-lg">
          <h2 className="h-sm"><Icon name="alert" size={20} /> {plural(failed.length, "problem")}</h2>
          <ul className="flist">
            {failed.map((a, i) => (
              <li key={i} className="frow static">
                <span className="fname">{baseName(a.src)}<span className="muted"> {a.error}</span></span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {detail && log.actions.length > 0 && (
        <section className="card pad-lg">
          <div className="title-row">
            <IconTile name={meta.icon} accent={meta.accent} size="sm" />
            <h2 className="h-sm">Every item ({log.actions.length})</h2>
          </div>
          <ul className="flist">
            {log.actions.slice(0, shown).map((a, i) => (
              <li key={i} className="frow static">
                <span className={`state ${a.status}`}><Icon name={label(a)} size={15} strokeWidth={3} /></span>
                <span className="fname">{baseName(a.src)}</span>
                {(a.final_dest || a.trashed_to) && (
                  <span className="dst"><Icon name="arrowRight" size={14} /> {a.trashed_to ? "Trash" : shortPath(a.final_dest!, home)}</span>
                )}
              </li>
            ))}
          </ul>
          {shown < log.actions.length && (
            <div className="list-foot">
              <span className="muted">Showing {shown} of {log.actions.length}</span>
              <button className="linklike" onClick={() => setShown((n) => n + 200)}>Show more</button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

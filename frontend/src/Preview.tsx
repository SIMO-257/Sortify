import { useMemo, useState } from "react";
import { api } from "./api";
import type { Log, Plan } from "./types";

type Props = { plan: Plan; onDone: (log: Log) => void; onBack: () => void };

const relative = (path: string, folder: string) => (path.startsWith(folder) ? path.slice(folder.length).replace(/^[\\/]/, "") : path);

export default function Preview({ plan, onDone, onBack }: Props) {
  const [selected, setSelected] = useState<Set<number>>(() => new Set(plan.actions.map((a) => a.id)));
  const [word, setWord] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showAll, setShowAll] = useState(false);

  const visible = useMemo(() => (showAll ? plan.actions : plan.actions.slice(0, 100)), [plan, showAll]);
  const toggle = (id: number) =>
    setSelected((current) => {
      const next = new Set(current);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  const ready = selected.size > 0 && (!plan.dangerous || word === "delete");

  const apply = async () => {
    setBusy(true);
    setError("");
    try {
      onDone(await api.apply(plan.plan_id, [...selected], plan.dangerous ? word : undefined));
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  };

  return (
    <div className="card stack">
      <h2>Preview</h2>
      <p className="muted">{plan.folder}</p>

      {plan.actions.length === 0 ? (
        <p>Nothing to do in this folder.</p>
      ) : (
        <>
          <ul className="groups">
            {plan.groups.map((g) => (
              <li key={g.name}>
                <strong>{g.count}</strong> {g.name}
              </li>
            ))}
          </ul>

          <div className="row">
            <button onClick={() => setSelected(new Set(plan.actions.map((a) => a.id)))}>Select all</button>
            <button onClick={() => setSelected(new Set())}>Select none</button>
            <span className="muted">
              {selected.size} of {plan.actions.length} selected
            </span>
          </div>

          <ul className="files">
            {visible.map((a) => (
              <li key={a.id}>
                <label className="check">
                  <input type="checkbox" checked={selected.has(a.id)} onChange={() => toggle(a.id)} />
                  <span className="file">
                    {relative(a.src, plan.folder)}
                    {a.dest && <span className="muted"> → {relative(a.dest, plan.folder)}</span>}
                  </span>
                </label>
              </li>
            ))}
          </ul>
          {!showAll && plan.actions.length > visible.length && (
            <button onClick={() => setShowAll(true)}>Show all {plan.actions.length} files</button>
          )}
        </>
      )}

      {plan.dangerous && plan.actions.length > 0 && (
        <label>
          <span>
            Deleted files go to the Sortify trash and can be undone. Type <code>delete</code> to confirm:
          </span>
          <input type="text" value={word} onChange={(e) => setWord(e.target.value.trim())} />
        </label>
      )}

      {error && <p className="error">{error}</p>}
      <div className="row end">
        <button onClick={onBack} disabled={busy}>
          Back
        </button>
        <button className={plan.dangerous ? "danger" : "primary"} disabled={!ready || busy} onClick={apply}>
          {busy ? "Working…" : plan.dangerous ? "Delete selected" : "Apply"}
        </button>
      </div>
    </div>
  );
}

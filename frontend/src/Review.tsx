import { useMemo, useState } from "react";
import { api } from "./api";
import { baseName, dirName, extAccent, extension, groupAccent, plural, relative, shortPath } from "./format";
import { Icon } from "./icons";
import { metaFor } from "./meta";
import type { Log, Plan } from "./types";
import { IconTile, Stat, type Notify } from "./ui";

type Props = { plan: Plan; operationName: string; home?: string; onBack: () => void; onDone: (log: Log) => void; notify: Notify };

const PAGE = 100;

export default function Review({ plan, operationName, home, onBack, onDone, notify }: Props) {
  const meta = metaFor(plan.operation);
  const [selected, setSelected] = useState<Set<number>>(() => new Set(plan.actions.map((a) => a.id)));
  const [word, setWord] = useState("");
  const [query, setQuery] = useState("");
  const [shown, setShown] = useState(PAGE);
  const [busy, setBusy] = useState(false);

  const moves = plan.actions[0]?.op === "move";
  const removes = plan.actions[0]?.op === "rmdir";
  const organizes = plan.operation.startsWith("organize");

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return needle ? plan.actions.filter((a) => relative(a.src, plan.folder).toLowerCase().includes(needle)) : plan.actions;
  }, [plan, query]);

  const toggle = (id: number) =>
    setSelected((current) => {
      const next = new Set(current);
      if (!next.delete(id)) next.add(id);
      return next;
    });

  const target = String(plan.options.target ?? "");
  const destination = (a: Plan["actions"][number]) => {
    if (a.op !== "move" || !a.dest) return null;
    const dir = dirName(a.dest);
    return organizes ? relative(dir, plan.folder) + "/" : shortPath(dir || target, home);
  };

  const apply = async () => {
    setBusy(true);
    try {
      onDone(await api.apply(plan.plan_id, [...selected], plan.dangerous ? word : undefined));
    } catch (e) {
      notify((e as Error).message);
      setBusy(false);
    }
  };

  const max = Math.max(1, ...plan.groups.map((g) => g.count));
  const folders = new Set(plan.actions.filter((a) => a.dest).map((a) => dirName(a.dest!))).size;
  const ready = selected.size > 0 && (!plan.dangerous || word === "delete");
  const noun = removes ? "folder" : "file";

  return (
    <div className="view">
      <div className="tiles">
        {moves && <Stat value={plan.actions.length} label={plan.actions.length === 1 ? "file to move" : "files to move"} />}
        {moves && <Stat value={folders} label={organizes ? "destination folders" : "target folder"} />}
        {moves && <Stat value={0} label="files overwritten" tone="ok" />}
        {plan.dangerous && <Stat value={plan.actions.length} label={plan.actions.length === 1 ? "file to delete" : "files to delete"} tone="warn" />}
        {plan.dangerous && <Stat value="Trash" label="not erased forever" />}
        {removes && <Stat value={plan.actions.length} label={plan.actions.length === 1 ? "empty folder" : "empty folders"} />}
        {removes && <Stat value={0} label="files affected" tone="ok" />}
        <Stat value="Undo" label="available after" tone="ok" />
      </div>

      <section className="card pad-lg">
        <div className="title-row">
          <IconTile name={meta.icon} accent={meta.accent} size="sm" />
          <div>
            <h2 className="h-sm">{operationName}</h2>
            <p className="muted mono">{shortPath(plan.folder, home)}</p>
          </div>
        </div>
        {plan.actions.length > 0 && (
          <>
            <span className="l spaced">{moves ? "Where files will go" : "What will change"}</span>
            <div className="bars">
              {plan.groups.map((g) => (
                <div className={`br ${groupAccent(g.name)}`} key={g.name}>
                  <span className="mono" title={g.name}>{g.name}</span>
                  <div className="trk"><div className="fil" style={{ width: `${(g.count / max) * 100}%` }} /></div>
                  <b>{g.count}</b>
                </div>
              ))}
            </div>
          </>
        )}
      </section>

      {plan.dangerous && plan.actions.length > 0 && (
        <section className="card pad-lg danger-card">
          <div className="title-row">
            <IconTile name="trash" accent="orange" />
            <div>
              <h2 className="h-sm">Delete {plural(selected.size, "file")}?</h2>
              <p className="muted">They move to the Sortify trash. You can undo this run later from the home screen or History.</p>
            </div>
          </div>
          <div className="note danger">
            <Icon name="lock" size={20} />
            <label htmlFor="confirm-word">Type <b className="mono">delete</b> to confirm</label>
          </div>
          <div className="field">
            <div className="input">
              <input id="confirm-word" type="text" value={word} autoComplete="off" spellCheck={false}
                placeholder="delete" onChange={(e) => setWord(e.target.value.trim().toLowerCase())}
                onKeyDown={(e) => e.key === "Enter" && ready && !busy && apply()} />
            </div>
          </div>
        </section>
      )}

      {plan.actions.length === 0 ? (
        <div className="empty big">
          <Icon name="sparkle" size={30} />
          <b>Nothing to do here</b>
          <span>This folder has nothing that matches. Go back and try another folder or option.</span>
          <button className="btn" onClick={onBack}><Icon name="arrowLeft" size={17} /> Back</button>
        </div>
      ) : (
        <section className="card pad-lg">
          <div className="toolbar">
            <div className="input search">
              <Icon name="search" size={18} />
              <input type="text" value={query} placeholder={`Search ${noun}s…`} aria-label={`Search ${noun}s`}
                onChange={(e) => { setQuery(e.target.value); setShown(PAGE); }} />
            </div>
            <button className="btn" onClick={() => setSelected(new Set(plan.actions.map((a) => a.id)))}>Select all</button>
            <button className="btn" onClick={() => setSelected(new Set())}>Select none</button>
          </div>

          <ul className="flist">
            {rows.slice(0, shown).map((a) => {
              const name = baseName(a.src);
              const ext = extension(name);
              const where = dirName(relative(a.src, plan.folder));
              const dest = destination(a);
              return (
                <li key={a.id}>
                  <label className="frow">
                    <input type="checkbox" className="cb" checked={selected.has(a.id)} onChange={() => toggle(a.id)} />
                    {removes ? (
                      <span className={`ext ${meta.accent}`}><Icon name="folder" size={14} /></span>
                    ) : (
                      <span className={`ext ${extAccent(ext)}`}>{ext ? `.${ext}` : "—"}</span>
                    )}
                    <span className="fname">
                      {name}
                      {where && <span className="muted"> in {where}</span>}
                    </span>
                    {dest && <span className="dst"><Icon name="arrowRight" size={14} /> {dest}</span>}
                    {a.op === "delete" && <span className="dst trash"><Icon name="arrowRight" size={14} /> Trash</span>}
                  </label>
                </li>
              );
            })}
          </ul>
          {rows.length === 0 && <p className="muted pad">No {noun}s match “{query}”.</p>}
          <div className="list-foot">
            <span className="muted">Showing {Math.min(shown, rows.length)} of {rows.length}</span>
            {shown < rows.length && (
              <button className="linklike" onClick={() => setShown((n) => n + 200)}>Show more</button>
            )}
          </div>
        </section>
      )}

      {plan.actions.length > 0 && (
        <div className="sticky">
          <button className="btn" onClick={onBack} disabled={busy}><Icon name="arrowLeft" size={17} /> Back</button>
          <span className="sp" />
          <span><b>{selected.size}</b> of {plan.actions.length} selected</span>
          <button className={`btn ${plan.dangerous ? "danger" : "primary"}`} disabled={!ready || busy} onClick={apply}>
            {busy ? "Working…" : plan.dangerous ? <><Icon name="trash" size={17} /> Delete selected</> : <>Apply changes</>}
          </button>
        </div>
      )}
    </div>
  );
}

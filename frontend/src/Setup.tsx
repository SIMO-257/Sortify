import { useEffect, useState } from "react";
import { api } from "./api";
import FolderField from "./FolderField";
import { shortPath } from "./format";
import { Icon } from "./icons";
import { example, metaFor } from "./meta";
import { recentFolders, rememberFolder } from "./storage";
import type { ExtensionCount, Operation, Plan } from "./types";
import { IconTile, Switch } from "./ui";

type Props = {
  operation: Operation;
  home?: string;
  initial?: { folder: string; options: Record<string, unknown> }; // restored when coming back from Review
  onPlan: (plan: Plan) => void;
  onBack: () => void;
};

export default function Setup({ operation, home, initial, onPlan, onBack }: Props) {
  const meta = metaFor(operation.id);
  const [folder, setFolder] = useState(initial?.folder ?? "");
  const [values, setValues] = useState<Record<string, unknown>>(() =>
    Object.fromEntries(
      operation.options.map((o) => [
        o.name,
        initial?.options[o.name] ?? (o.type === "bool" ? !!o.default : o.type === "extension" ? null : ""),
      ]),
    ),
  );
  const [extensions, setExtensions] = useState<ExtensionCount[] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const recent = recentFolders();

  const set = (name: string, value: unknown) => setValues((v) => ({ ...v, [name]: value }));
  const needsExtension = operation.options.some((o) => o.type === "extension");
  const recursive = !!values.recursive;

  useEffect(() => {
    if (!needsExtension || !folder.trim()) {
      setExtensions(null);
      return;
    }
    const timer = setTimeout(() => {
      api
        .extensions(folder, recursive)
        .then((found) => {
          setExtensions(found);
          setError("");
          setValues((v) => (found.some((f) => f.extension === v.extension) ? v : { ...v, extension: null }));
        })
        .catch((e: Error) => {
          setExtensions(null);
          setError(e.message);
        });
    }, 400);
    return () => clearTimeout(timer);
  }, [folder, recursive, needsExtension]);

  const ready =
    folder.trim() !== "" &&
    operation.options.every((o) => {
      if (!o.required) return true;
      const value = values[o.name];
      return o.type === "extension" ? typeof value === "string" : String(value ?? "").trim() !== "";
    });

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!ready || busy) return;
    setBusy(true);
    setError("");
    try {
      const options = Object.fromEntries(
        Object.entries(values).map(([k, v]) => [k, typeof v === "string" ? v.trim() : v]),
      );
      const plan = await api.plan(operation.id, folder.trim(), options);
      rememberFolder(plan.folder);
      onPlan(plan);
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  };

  const demo = example(operation.id, values);

  return (
    <div className="view two">
      <form onSubmit={submit} className="card pad-lg stack">
        <div className="title-row">
          <IconTile name={meta.icon} accent={meta.accent} />
          <div>
            <h2>{operation.name}</h2>
            <p className="muted">{meta.lead}</p>
          </div>
        </div>

        <FolderField label="Folder" value={folder} onChange={setFolder} autoFocus />
        {recent.length > 0 && (
          <div className="chips tight">
            <span className="chip plain"><Icon name="clock" size={14} /> Recent</span>
            {recent.map((path) => (
              <button type="button" key={path} className="chip mono" onClick={() => setFolder(path)} title={path}>
                {shortPath(path, home)}
              </button>
            ))}
          </div>
        )}

        {operation.options.map((option) => {
          if (option.type === "bool") {
            return (
              <Switch key={option.name} checked={!!values[option.name]} onChange={(v) => set(option.name, v)}>
                {option.label}
              </Switch>
            );
          }
          if (option.type === "extension") {
            return (
              <div key={option.name} className="field-group">
                <span className="l">{option.label}</span>
                {extensions === null && <p className="muted">Choose a folder first to see the file types in it.</p>}
                {extensions?.length === 0 && <p className="muted">No files found in this folder.</p>}
                <div className="chips">
                  {extensions?.map((e) => (
                    <button type="button" key={e.extension} aria-pressed={values[option.name] === e.extension}
                      className={`chip ${values[option.name] === e.extension ? "sel" : ""}`}
                      onClick={() => set(option.name, e.extension)}>
                      {e.extension || "(no extension)"} <small>{e.count}</small>
                    </button>
                  ))}
                </div>
              </div>
            );
          }
          if (option.type === "folder") {
            return (
              <FolderField key={option.name} label={option.label} pickerTitle="Where should the files go?"
                value={String(values[option.name])} onChange={(v) => set(option.name, v)} />
            );
          }
          return (
            <div key={option.name} className="field-group">
              <label className="l" htmlFor={`opt-${option.name}`}>{option.label}</label>
              <div className="field">
                <div className="input">
                  <input id={`opt-${option.name}`} type="text" value={String(values[option.name])} spellCheck={false}
                    onChange={(e) => set(option.name, e.target.value)} />
                </div>
              </div>
              {option.name === "label" && <p className="muted hint">Folders will be named like <code>{String(demo.after[0]?.name)}</code>.</p>}
            </div>
          );
        })}

        {error && <p className="note bad"><Icon name="alert" size={18} /> {error}</p>}

        <div className="row between">
          <button type="button" className="btn" onClick={onBack}><Icon name="arrowLeft" size={17} /> Back</button>
          <button className="btn primary" disabled={!ready || busy}>
            {busy ? "Scanning…" : <>Preview <Icon name="arrowRight" size={17} /></>}
          </button>
        </div>
      </form>

      <aside className="card pad-lg ba" aria-label="What will happen">
        <div className="ba-title"><Icon name="sparkle" size={19} /> What will happen</div>
        <Tree title="Before" rows={demo.before} />
        <div className="ba-arrow"><Icon name="arrowRight" size={20} style={{ transform: "rotate(90deg)" }} /></div>
        <Tree title="After" rows={demo.after} />
        <p className="muted hint">An example only. Your real files are shown on the next screen before anything changes.</p>
      </aside>
    </div>
  );
}

function Tree({ title, rows }: { title: string; rows: ReturnType<typeof example>["before"] }) {
  return (
    <div className="box">
      <b>{title}</b>
      <ul>
        {rows.map((row, i) => (
          <li key={i} className={`${row.level ? "lvl" : ""} ${row.faded ? "faded" : ""}`}>
            <Icon name={row.kind === "folder" ? "folder" : "documents"} size={16} />
            {row.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

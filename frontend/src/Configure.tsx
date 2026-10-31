import { useEffect, useState } from "react";
import { api } from "./api";
import FolderInput from "./FolderInput";
import type { ExtensionCount, Operation, Plan } from "./types";

type Props = { operation: Operation; onPlan: (plan: Plan) => void; onBack: () => void };

export default function Configure({ operation, onPlan, onBack }: Props) {
  const [folder, setFolder] = useState("");
  const [values, setValues] = useState<Record<string, unknown>>(() =>
    Object.fromEntries(
      operation.options.map((o) => [o.name, o.type === "bool" ? !!o.default : o.type === "extension" ? "__none__" : ""]),
    ),
  );
  const [extensions, setExtensions] = useState<ExtensionCount[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const needsExtension = operation.options.some((o) => o.type === "extension");
  const recursive = !!values.recursive;
  const set = (name: string, value: unknown) => setValues((v) => ({ ...v, [name]: value }));

  useEffect(() => {
    if (!needsExtension || !folder.trim()) {
      setExtensions([]);
      return;
    }
    const timer = setTimeout(() => {
      api
        .extensions(folder, recursive)
        .then((found) => {
          setExtensions(found);
          setError("");
          if (!found.some((f) => f.extension === values.extension)) set("extension", "__none__");
        })
        .catch((e: Error) => {
          setExtensions([]);
          setError(e.message);
        });
    }, 400);
    return () => clearTimeout(timer);
  }, [folder, recursive, needsExtension]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const options = { ...values };
      if (options.extension === "__none__") {
        setError("Choose an extension.");
        return;
      }
      onPlan(await api.plan(operation.id, folder, options));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="card stack">
      <h2>{operation.name}</h2>
      <p className="muted">{operation.description}</p>

      <label>
        Folder
        <FolderInput value={folder} onChange={setFolder} />
      </label>

      {operation.options.map((option) => {
        if (option.type === "bool") {
          return (
            <label key={option.name} className="check">
              <input type="checkbox" checked={!!values[option.name]} onChange={(e) => set(option.name, e.target.checked)} />
              {option.label}
            </label>
          );
        }
        if (option.type === "extension") {
          return (
            <label key={option.name}>
              {option.label}
              <select
                value={String(values[option.name])}
                onChange={(e) => set(option.name, e.target.value)}
                disabled={extensions.length === 0}
              >
                <option value="__none__">{extensions.length ? "Choose…" : "Enter a folder first"}</option>
                {extensions.map((e) => (
                  <option key={e.extension} value={e.extension}>
                    {e.extension || "(no extension)"} — {e.count} files
                  </option>
                ))}
              </select>
            </label>
          );
        }
        if (option.type === "folder") {
          return (
            <label key={option.name}>
              {option.label}
              <FolderInput value={String(values[option.name])} onChange={(v) => set(option.name, v)} />
            </label>
          );
        }
        return (
          <label key={option.name}>
            {option.label}
            <input type="text" value={String(values[option.name])} onChange={(e) => set(option.name, e.target.value)} />
          </label>
        );
      })}

      {error && <p className="error">{error}</p>}
      <div className="row end">
        <button type="button" onClick={onBack}>
          Back
        </button>
        <button className="primary" disabled={busy || !folder.trim()}>
          {busy ? "Scanning…" : "Preview"}
        </button>
      </div>
    </form>
  );
}

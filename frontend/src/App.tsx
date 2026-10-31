import { useEffect, useState } from "react";
import { api, hasToken } from "./api";
import Configure from "./Configure";
import History from "./History";
import Preview from "./Preview";
import Result from "./Result";
import type { Log, Operation, Plan } from "./types";

type View =
  | { name: "home" }
  | { name: "configure"; operation: Operation }
  | { name: "preview"; plan: Plan }
  | { name: "result"; log: Log }
  | { name: "history" }
  | { name: "run"; log: Log };

export default function App() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [view, setView] = useState<View>({ name: "home" });
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasToken()) return;
    api.operations().then(setOperations).catch((e: Error) => setError(e.message));
  }, []);

  const home = () => setView({ name: "home" });

  if (!hasToken()) {
    return (
      <main>
        <h1>Sortify</h1>
        <p className="error">
          This page needs the private link printed in the terminal where Sortify is running (it ends with
          <code> #token=…</code>). Open that link instead.
        </p>
      </main>
    );
  }

  return (
    <main>
      <header className="row">
        <h1 onClick={home} className="title">
          Sortify
        </h1>
        <button onClick={() => setView({ name: "history" })}>History</button>
      </header>

      {error && <p className="error">{error}</p>}

      {view.name === "home" && (
        <div className="grid">
          {operations.map((operation) => (
            <button key={operation.id} className="card op" onClick={() => setView({ name: "configure", operation })}>
              <strong>{operation.name}</strong>
              <span className="muted">{operation.description}</span>
            </button>
          ))}
        </div>
      )}

      {view.name === "configure" && (
        <Configure
          operation={view.operation}
          onBack={home}
          onPlan={(plan) => setView({ name: "preview", plan })}
        />
      )}

      {view.name === "preview" && (
        <Preview plan={view.plan} onBack={home} onDone={(log) => setView({ name: "result", log })} />
      )}

      {view.name === "result" && (
        <Result log={view.log} closeLabel="Start over" onClose={home} onUndone={(log) => setView({ name: "result", log })} />
      )}

      {view.name === "history" && (
        <History
          onBack={home}
          onOpen={(id) => api.log(id).then((log) => setView({ name: "run", log })).catch((e: Error) => setError(e.message))}
        />
      )}

      {view.name === "run" && (
        <Result
          log={view.log}
          closeLabel="Back to history"
          onClose={() => setView({ name: "history" })}
          onUndone={(log) => setView({ name: "run", log })}
        />
      )}
    </main>
  );
}

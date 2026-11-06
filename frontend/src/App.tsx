import { useCallback, useEffect, useState } from "react";
import { api, hasToken } from "./api";
import Done from "./Done";
import History from "./History";
import Home from "./Home";
import NoToken from "./NoToken";
import Review from "./Review";
import Setup from "./Setup";
import type { Log, Operation, Plan } from "./types";
import { Header, Stepper, Toasts, type Notify, type Toast } from "./ui";

type View =
  | { name: "home" }
  | { name: "setup"; operation: Operation; initial?: { folder: string; options: Record<string, unknown> } }
  | { name: "review"; plan: Plan }
  | { name: "done"; log: Log }
  | { name: "history" }
  | { name: "run"; log: Log };

const STEP: Partial<Record<View["name"], number>> = { setup: 1, review: 2, done: 3 };

export default function App() {
  if (!hasToken()) return <NoToken />;
  return <Shell />;
}

function Shell() {
  const [operations, setOperations] = useState<Operation[] | null>(null);
  const [home, setHome] = useState<string>();
  const [view, setView] = useState<View>({ name: "home" });
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => setToasts((all) => all.filter((t) => t.id !== id)), []);
  const notify: Notify = useCallback(
    (text, kind = "error") => {
      const id = Date.now() + Math.random();
      setToasts((all) => [...all.slice(-2), { id, kind, text }]);
      setTimeout(() => dismiss(id), kind === "error" ? 7000 : 4000);
    },
    [dismiss],
  );

  useEffect(() => {
    api.operations().then(setOperations).catch((e: Error) => { setOperations([]); notify(e.message); });
    api.browse("", false).then((r) => setHome(r.shortcuts.find((s) => s.name === "Home")?.path)).catch(() => {});
  }, [notify]);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [view.name]);

  const goHome = () => setView({ name: "home" });
  const nameOf = (id: string) => operations?.find((o) => o.id === id)?.name ?? id;
  const openRun = (id: string) =>
    api.log(id).then((log) => setView({ name: "run", log })).catch((e: Error) => notify(e.message));

  const step = STEP[view.name];

  return (
    <main className="wrap">
      <Header onHome={goHome} onHistory={() => setView({ name: "history" })} historyActive={view.name === "history" || view.name === "run"} />
      {step !== undefined && <Stepper active={step} />}

      {view.name === "home" && <Home operations={operations} home={home} onPick={(operation) => setView({ name: "setup", operation })} onOpenRun={openRun} notify={notify} />}
      {view.name === "setup" && <Setup key={view.operation.id} operation={view.operation} initial={view.initial} home={home} onBack={goHome} onPlan={(plan) => setView({ name: "review", plan })} />}
      {view.name === "review" && (
        <Review plan={view.plan} operationName={nameOf(view.plan.operation)} home={home} notify={notify}
          onBack={() => setView({ name: "setup", operation: operations!.find((o) => o.id === view.plan.operation)!, initial: { folder: view.plan.folder, options: view.plan.options } })}
          onDone={(log) => setView({ name: "done", log })} />
      )}
      {view.name === "done" && <Done log={view.log} operationName={nameOf(view.log.operation)} home={home} notify={notify} closeLabel="Start another" onClose={goHome} onUndone={(log) => setView({ name: "done", log })} />}
      {view.name === "history" && <History operations={operations} home={home} onOpen={openRun} onError={notify} />}
      {view.name === "run" && <Done detail log={view.log} operationName={nameOf(view.log.operation)} home={home} notify={notify} closeLabel="Back to history" onClose={() => setView({ name: "history" })} onUndone={(log) => setView({ name: "run", log })} />}

      <Toasts toasts={toasts} onDismiss={dismiss} />
    </main>
  );
}

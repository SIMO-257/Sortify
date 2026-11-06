import type { ReactNode } from "react";
import { Icon, type IconName } from "./icons";
import Logo from "./Logo";

export const STEPS = ["Choose", "Setup", "Review", "Done"];

export function Stepper({ active }: { active: number }) {
  return (
    <ol className="stepper" aria-label="Progress">
      {STEPS.map((name, i) => {
        const state = i < active ? "done" : i === active ? "act" : "";
        return (
          <li key={name} className={`step ${state}`} aria-current={i === active ? "step" : undefined}>
            <span className="dot">{i < active ? <Icon name="check" size={14} strokeWidth={3} /> : i + 1}</span>
            <span className="step-name">{name}</span>
            {i < STEPS.length - 1 && <span className={`bar ${i < active ? "done" : ""}`} />}
          </li>
        );
      })}
    </ol>
  );
}

export function Header({ onHome, onHistory, historyActive }: { onHome: () => void; onHistory: () => void; historyActive: boolean }) {
  return (
    <header className="top">
      <button className="brand" onClick={onHome} aria-label="Sortify home">
        <Logo />
        <span>Sortify</span>
      </button>
      <button className={`btn ${historyActive ? "pressed" : ""}`} onClick={onHistory}>
        <Icon name="clock" size={17} /> History
      </button>
    </header>
  );
}

export function Switch({ checked, onChange, children }: { checked: boolean; onChange: (value: boolean) => void; children: ReactNode }) {
  return (
    <button type="button" role="switch" aria-checked={checked} className="toggle" onClick={() => onChange(!checked)}>
      <span className={`sw ${checked ? "on" : ""}`} />
      <span>{children}</span>
    </button>
  );
}

export function IconTile({ name, accent, size = "md" }: { name: IconName; accent: string; size?: "sm" | "md" | "lg" }) {
  return (
    <span className={`ico ${accent} ${size}`}>
      <Icon name={name} size={size === "sm" ? 18 : size === "lg" ? 30 : 24} />
    </span>
  );
}

export function Stat({ value, label, tone }: { value: ReactNode; label: string; tone?: "ok" | "warn" | "bad" }) {
  return (
    <div className="tile">
      <b className={tone}>{value}</b>
      <span>{label}</span>
    </div>
  );
}

export type Toast = { id: number; kind: "error" | "success"; text: string };

export function Toasts({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  return (
    <div className="toasts" role="status" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.kind}`}>
          <Icon name={t.kind === "error" ? "alert" : "checkCircle"} size={20} />
          <span>{t.text}</span>
          <button className="x" aria-label="Dismiss" onClick={() => onDismiss(t.id)}>
            <Icon name="x" size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

export type Notify = (text: string, kind?: Toast["kind"]) => void;

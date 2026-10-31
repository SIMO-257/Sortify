import { useState } from "react";
import FolderPicker from "./FolderPicker";

type Props = { value: string; onChange: (path: string) => void; placeholder?: string };

export default function FolderInput({ value, onChange, placeholder }: Props) {
  const [picking, setPicking] = useState(false);
  return (
    <div className="row">
      <input
        type="text"
        value={value}
        placeholder={placeholder ?? "Paste a folder path"}
        onChange={(e) => onChange(e.target.value)}
      />
      <button type="button" onClick={() => setPicking(true)}>
        Browse…
      </button>
      {picking && (
        <FolderPicker
          start={value}
          onClose={() => setPicking(false)}
          onPick={(path) => {
            onChange(path);
            setPicking(false);
          }}
        />
      )}
    </div>
  );
}

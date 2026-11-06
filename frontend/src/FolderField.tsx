import { useState } from "react";
import FolderPicker from "./FolderPicker";
import { Icon } from "./icons";

type Props = { value: string; onChange: (path: string) => void; label: string; pickerTitle?: string; autoFocus?: boolean };

export default function FolderField({ value, onChange, label, pickerTitle, autoFocus }: Props) {
  const [picking, setPicking] = useState(false);
  return (
    <div className="field-group">
      <label className="l" htmlFor={`folder-${label}`}>{label}</label>
      <div className="field">
        <div className="input">
          <Icon name="folder" size={20} />
          <input id={`folder-${label}`} type="text" value={value} autoFocus={autoFocus} spellCheck={false}
            placeholder="Paste a folder path or press Browse" onChange={(e) => onChange(e.target.value)} />
        </div>
        <button type="button" className="btn" onClick={() => setPicking(true)}>
          <Icon name="folder" size={17} /> Browse…
        </button>
      </div>
      {picking && (
        <FolderPicker start={value} title={pickerTitle} onClose={() => setPicking(false)}
          onPick={(path) => { onChange(path); setPicking(false); }} />
      )}
    </div>
  );
}

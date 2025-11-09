import type { FormEvent } from "react";
import { useMemo, useState } from "react";

interface ExcludeDirsSectionProps {
  defaultDirs: readonly string[];
  customDirs: string[];
  disabled: boolean;
  onAdd: (value: string) => { ok: boolean; error?: string };
  onRemove: (value: string) => void;
}

export function ExcludeDirsSection({
  defaultDirs,
  customDirs,
  disabled,
  onAdd,
  onRemove,
}: ExcludeDirsSectionProps): JSX.Element {
  const [inputValue, setInputValue] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const hasCustom = customDirs.length > 0;

  const defaultLabel = useMemo(
    () =>
      defaultDirs.length > 4
        ? `${defaultDirs.slice(0, 4).join(", ")}…`
        : defaultDirs.join(", "),
    [defaultDirs],
  );

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFeedback(null);

    const trimmed = inputValue.trim();
    if (!trimmed) {
      setFeedback("Enter a valid directory name.");
      return;
    }

    const result = onAdd(trimmed);
    if (!result.ok) {
      setFeedback(result.error ?? "Could not add the directory.");
      return;
    }

    setInputValue("");
    setFeedback(null);
  };

  return (
    <section className="settings-card">
      <h2>Exclusions</h2>
      <p>Customize the directories ignored during scans.</p>

      <div className="settings-tags" title={defaultLabel}>
        {defaultDirs.map((dir) => (
          <span className="settings-tag settings-tag--locked" key={dir}>
            {dir}
          </span>
        ))}
      </div>

      {hasCustom ? (
        <div className="settings-tags">
          {customDirs.map((dir) => (
            <span className="settings-tag settings-tag--custom" key={dir}>
              {dir}
              <button
                type="button"
                className="settings-tag__remove"
                onClick={() => onRemove(dir)}
                aria-label={`Remove ${dir} from exclusions`}
                disabled={disabled}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      ) : (
        <p className="settings-helper">You haven't added any custom exclusions yet.</p>
      )}

      <form className="exclude-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder="e.g. build, coverage, tmp"
          disabled={disabled}
        />
        <button type="submit" className="primary-btn" disabled={disabled}>
          Add
        </button>
      </form>

      {feedback && <p className="settings-helper settings-helper--error">{feedback}</p>}
      <p className="settings-helper">
        Only provide a directory name (no absolute paths). Values are stored alongside the project's
        default exclusions.
      </p>
    </section>
  );
}

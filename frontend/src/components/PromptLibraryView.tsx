import { useEffect, useMemo, useState } from "react";

import { usePromptLibrary, type PromptEntry } from "../state/usePromptLibrary";

const PROMPT_CATEGORIES = ["Design", "Architect", "Review", "Debug", "Develop", "Documentation"] as const;

type CopyState = "idle" | "copied" | "error";

function parseTagsInput(raw: string): string[] {
  return raw
    .split(/[,;#\n]+/)
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
}

function formatDate(value?: string | null): string {
  if (!value) {
    return "—";
  }
  try {
    return new Date(value).toLocaleString("en-US");
  } catch {
    return value;
  }
}

export function PromptLibraryView(): JSX.Element {
  const { prompts, addPrompt, updatePrompt, deletePrompt, recordUsage } = usePromptLibrary();

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(
    prompts.length > 0 ? prompts[0]?.id ?? null : null
  );
  const [copyState, setCopyState] = useState<CopyState>("idle");

  const [createDraft, setCreateDraft] = useState({
    title: "",
    body: "",
    tags: "",
    category: "",
    notes: "",
  });

  const selectedPrompt: PromptEntry | undefined = useMemo(
    () => prompts.find((prompt) => prompt.id === selectedPromptId),
    [prompts, selectedPromptId]
  );

  useEffect(() => {
    if (selectedPromptId && !selectedPrompt && prompts.length > 0) {
      setSelectedPromptId(prompts[0]?.id ?? null);
    }
  }, [prompts, selectedPrompt, selectedPromptId]);

  const [editDraft, setEditDraft] = useState({
    title: "",
    body: "",
    tags: "",
    category: "",
    notes: "",
  });

  useEffect(() => {
    if (!selectedPrompt) {
      setEditDraft({
        title: "",
        body: "",
        tags: "",
        category: "",
        notes: "",
      });
      return;
    }
    setEditDraft({
      title: selectedPrompt.title,
      body: selectedPrompt.body,
      tags: selectedPrompt.tags.join(", "),
      category: selectedPrompt.category ?? "",
      notes: selectedPrompt.notes ?? "",
    });
  }, [selectedPrompt]);

  useEffect(() => {
    if (copyState === "idle") {
      return;
    }
    const timeout = setTimeout(() => setCopyState("idle"), 2200);
    return () => clearTimeout(timeout);
  }, [copyState]);

  const allTags = useMemo(() => {
    const tags = new Set<string>();
    prompts.forEach((prompt) => {
      prompt.tags.forEach((tag) => tags.add(tag));
    });
    return Array.from(tags).sort((a, b) => a.localeCompare(b));
  }, [prompts]);

  const filteredPrompts = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    const tag = selectedTag;
    return prompts.filter((prompt) => {
      if (tag && !prompt.tags.includes(tag)) {
        return false;
      }
      if (!term) {
        return true;
      }
      const haystack = [prompt.title, prompt.body, prompt.notes ?? "", ...prompt.tags].join(" ");
      return haystack.toLowerCase().includes(term);
    });
  }, [prompts, searchTerm, selectedTag]);

  useEffect(() => {
    if (!filteredPrompts.some((prompt) => prompt.id === selectedPromptId)) {
      setSelectedPromptId(filteredPrompts[0]?.id ?? null);
    }
  }, [filteredPrompts, selectedPromptId]);

  const hasCreateDraft =
    createDraft.title.trim().length > 0 && createDraft.body.trim().length > 0;

  const hasChanges =
    selectedPrompt &&
    (selectedPrompt.title !== editDraft.title ||
      selectedPrompt.body !== editDraft.body ||
      (selectedPrompt.category ?? "") !== editDraft.category ||
      (selectedPrompt.notes ?? "") !== editDraft.notes ||
      selectedPrompt.tags.join(", ") !==
        parseTagsInput(editDraft.tags)
          .map((tag) => tag.toLowerCase())
          .join(", "));

  const handleCreatePrompt = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!hasCreateDraft) {
      return;
    }
    const id = addPrompt({
      title: createDraft.title,
      body: createDraft.body,
      tags: parseTagsInput(createDraft.tags),
      category: createDraft.category || undefined,
      notes: createDraft.notes || undefined,
    });
    setCreateDraft({ title: "", body: "", tags: "", category: "", notes: "" });
    setSelectedPromptId(id);
  };

  const handleSaveChanges = () => {
    if (!selectedPrompt) {
      return;
    }
    updatePrompt(selectedPrompt.id, {
      title: editDraft.title,
      body: editDraft.body,
      tags: parseTagsInput(editDraft.tags),
      category: editDraft.category || undefined,
      notes: editDraft.notes || undefined,
    });
  };

  const handleDeletePrompt = () => {
    if (!selectedPrompt) {
      return;
    }
    const confirmed = window.confirm(
      `Delete the prompt "${selectedPrompt.title}"? This action cannot be undone.`
    );
    if (!confirmed) {
      return;
    }
    deletePrompt(selectedPrompt.id);
    setSelectedPromptId(null);
  };

  const handleCopyPrompt = async () => {
    if (!selectedPrompt) {
      return;
    }
    try {
      await navigator.clipboard.writeText(selectedPrompt.body);
      recordUsage(selectedPrompt.id);
      setCopyState("copied");
    } catch {
      setCopyState("error");
    }
  };

  return (
    <div className="prompts-view">
      <section className="prompts-hero">
        <div>
          <h2>Prompt Library</h2>
          <p>
            Save recurring prompts and access them quickly for your agent workflows. Organize with
            tags, add notes, and copy with a single click.
          </p>
        </div>
        <div className="prompts-hero__meta">
          <span>
            Saved prompts: <strong>{prompts.length.toLocaleString("en-US")}</strong>
          </span>
          <span>
            Tags: <strong>{allTags.length}</strong>
          </span>
        </div>
      </section>

      <section className="prompts-create">
        <h3>New prompt</h3>
        <form className="prompts-create__form" onSubmit={handleCreatePrompt}>
          <div className="prompts-create__row">
            <label>
              Title
              <input
                type="text"
                value={createDraft.title}
                onChange={(event) =>
                  setCreateDraft((draft) => ({ ...draft, title: event.target.value }))
                }
                placeholder="E.g. explain a bug to a teammate"
                required
              />
            </label>
            <label>
              Tags
              <input
                type="text"
                value={createDraft.tags}
                onChange={(event) =>
                  setCreateDraft((draft) => ({ ...draft, tags: event.target.value }))
                }
                placeholder="E.g. communication, summary"
              />
            </label>
            <label>
              Category
              <select
                value={createDraft.category}
                onChange={(event) =>
                  setCreateDraft((draft) => ({ ...draft, category: event.target.value }))
                }
              >
                <option value="">No category</option>
                {PROMPT_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            Content
            <textarea
              value={createDraft.body}
              onChange={(event) =>
                setCreateDraft((draft) => ({ ...draft, body: event.target.value }))
              }
              placeholder="Write the full prompt here…"
              rows={7}
              required
            />
          </label>
          <label>
            Notes
            <textarea
              value={createDraft.notes}
              onChange={(event) =>
                setCreateDraft((draft) => ({ ...draft, notes: event.target.value }))
              }
              placeholder="Additional details or usage context (optional)…"
              rows={3}
            />
          </label>
          <div className="prompts-create__actions">
            <button className="primary-btn" type="submit" disabled={!hasCreateDraft}>
              Save prompt
            </button>
            <span className="prompts-hint">
              Separate tags with commas, semicolons, or newlines.
            </span>
          </div>
        </form>
      </section>

      <section className="prompts-content">
        <aside className="prompts-sidebar">
          <div className="prompts-sidebar__controls">
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by title, content, or tag…"
            />
            <div className="prompts-tags">
              <button
                type="button"
                className={`prompts-tag ${selectedTag === null ? "is-active" : ""}`}
                onClick={() => setSelectedTag(null)}
              >
                All
              </button>
              {allTags.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  className={`prompts-tag ${selectedTag === tag ? "is-active" : ""}`}
                  onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>

          <div className="prompts-list">
            {filteredPrompts.length === 0 ? (
              <p className="prompts-empty">
                No prompts match the current filters.
              </p>
            ) : (
              filteredPrompts.map((prompt) => (
                <button
                  key={prompt.id}
                  type="button"
                  className={`prompts-list__item${
                    prompt.id === selectedPromptId ? " is-selected" : ""
                  }`}
                  onClick={() => setSelectedPromptId(prompt.id)}
                >
                  <span className="prompts-list__title">{prompt.title}</span>
                  <span className="prompts-list__meta">
                    <span>
                      {prompt.category ?? "No category"}
                      {prompt.tags.length > 0
                        ? ` · ${prompt.tags
                            .slice(0, 3)
                            .map((tag) => `#${tag}`)
                            .join(" · ")}`
                        : ""}
                    </span>
                    <span>Updated: {formatDate(prompt.updatedAt)}</span>
                  </span>
                </button>
              ))
            )}
          </div>
        </aside>

        <div className="prompts-detail">
          {!selectedPrompt ? (
            <div className="prompts-detail__empty">
              <p>Select a prompt from the list to view its contents.</p>
            </div>
          ) : (
            <div className="prompts-detail__content">
              <header className="prompts-detail__header">
                <div>
                  <input
                    className="prompts-detail__title"
                    type="text"
                    value={editDraft.title}
                    onChange={(event) =>
                      setEditDraft((draft) => ({ ...draft, title: event.target.value }))
                    }
                  />
                  <div className="prompts-detail__chips">
                    {selectedPrompt.category ? (
                      <span className="prompts-chip prompts-chip--category">
                        {selectedPrompt.category}
                      </span>
                    ) : null}
                    {selectedPrompt.tags.map((tag) => (
                      <span key={tag} className="prompts-chip">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="prompts-detail__actions">
                  <button className="secondary-btn" type="button" onClick={handleCopyPrompt}>
                    Copy
                  </button>
                  <button className="secondary-btn" type="button" onClick={handleSaveChanges} disabled={!hasChanges}>
                    Save changes
                  </button>
                  <button className="danger-btn" type="button" onClick={handleDeletePrompt}>
                    Delete
                  </button>
                </div>
              </header>

              <label>
                Content
                <textarea
                  value={editDraft.body}
                  onChange={(event) =>
                    setEditDraft((draft) => ({ ...draft, body: event.target.value }))
                  }
                  rows={14}
                />
              </label>

              <div className="prompts-detail__grid">
                <label>
                  Tags
                  <input
                    type="text"
                    value={editDraft.tags}
                    onChange={(event) =>
                      setEditDraft((draft) => ({ ...draft, tags: event.target.value }))
                    }
                    placeholder="Product, retro, documentation…"
                  />
                </label>
                <label>
                  Category
                  <select
                    value={editDraft.category}
                    onChange={(event) =>
                      setEditDraft((draft) => ({ ...draft, category: event.target.value }))
                    }
                  >
                    <option value="">No category</option>
                    {PROMPT_CATEGORIES.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Notes
                  <textarea
                    value={editDraft.notes}
                    onChange={(event) =>
                      setEditDraft((draft) => ({ ...draft, notes: event.target.value }))
                    }
                    rows={4}
                  />
                </label>
              </div>

              <footer className="prompts-detail__footer">
                <div>
                  <span>Created: {formatDate(selectedPrompt.createdAt)}</span>
                  <span>Updated: {formatDate(selectedPrompt.updatedAt)}</span>
                  <span>Last used: {formatDate(selectedPrompt.lastUsedAt)}</span>
                </div>
                {copyState !== "idle" ? (
                  <span className={`prompts-copy-state prompts-copy-state--${copyState}`}>
                    {copyState === "copied"
                      ? "Prompt copied to clipboard."
                      : "Could not copy the prompt."}
                  </span>
                ) : null}
              </footer>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import type {
  AgentInstallStatus,
  DocsStatus,
  StageAgentSelection,
  StageDetectionStatus,
} from "../api/types";
import { useStageInitMutation } from "../hooks/useStageInitMutation";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";

const AGENT_OPTIONS: { value: StageAgentSelection; label: string }[] = [
  { value: "both", label: "Claude + Codex" },
  { value: "claude", label: "Claude only" },
  { value: "codex", label: "Codex only" },
];

function formatList(values: string[]): JSX.Element {
  if (values.length === 0) {
    return <em>—</em>;
  }

  return (
    <ul className="stage-list">
      {values.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function AgentStatusCard({
  title,
  status,
}: {
  title: string;
  status: AgentInstallStatus | undefined;
}): JSX.Element {
  if (!status) {
    return (
      <article className="stage-card">
        <header>
          <h3>{title}</h3>
        </header>
        <p>Unable to retrieve status.</p>
      </article>
    );
  }

  const badgeClass = status.installed ? "stage-badge success" : "stage-badge warn";
  const badgeLabel = status.installed ? "Installed" : "Missing items";

  return (
    <article className="stage-card">
      <header>
        <h3>{title}</h3>
        <span className={badgeClass}>{badgeLabel}</span>
      </header>
      <section>
        <h4>Present files</h4>
        {formatList(status.present)}
      </section>
      <section>
        <h4>Missing files</h4>
        {formatList(status.missing)}
      </section>
      {status.optional && status.optional.expected.length > 0 ? (
        <section>
          <h4>Optional files</h4>
          {status.optional.missing.length === 0 ? (
            <p className="stage-optional">All optional files are present.</p>
          ) : (
            <>
              <p className="stage-optional">
                Recommended optional files that are not strictly required:
              </p>
              {formatList(status.optional.missing)}
            </>
          )}
        </section>
      ) : null}
    </article>
  );
}

function DocsStatusCard({ status }: { status: DocsStatus | undefined }): JSX.Element {
  if (!status) {
    return (
      <article className="stage-card">
        <header>
          <h3>Documentation</h3>
        </header>
        <p>Could not inspect the docs/ folder.</p>
      </article>
    );
  }
  const badgeClass = status.complete ? "stage-badge success" : "stage-badge warn";
  const badgeLabel = status.complete ? "Complete" : "Missing files";

  return (
    <article className="stage-card">
      <header>
        <h3>Documentation</h3>
        <span className={badgeClass}>{badgeLabel}</span>
      </header>
      <section>
        <h4>Present</h4>
        {formatList(status.present)}
      </section>
      <section>
        <h4>Missing</h4>
        {formatList(status.missing)}
      </section>
    </article>
  );
}

function StageDetectionCard({ detection }: { detection: StageDetectionStatus | undefined }) {
  if (!detection) {
    return null;
  }
  const { available, recommended_stage, confidence, reasons, metrics, error, checked_at } = detection;

  if (!available) {
    return (
      <article className="stage-card">
        <header>
          <h3>Stage detection</h3>
          <span className="stage-badge warn">Unavailable</span>
        </header>
        <p>{error ?? "The project stage could not be evaluated."}</p>
      </article>
    );
  }

  return (
    <article className="stage-card stage-detection">
      <header>
        <h3>Stage detection</h3>
        <span className="stage-badge success">
          Stage {recommended_stage} · {confidence?.toUpperCase() ?? "N/A"}
        </span>
      </header>
      {checked_at ? (
        <p className="stage-meta">Last check: {new Date(checked_at).toLocaleString()}</p>
      ) : null}
      <section>
        <h4>Key reasons</h4>
        {formatList(reasons)}
      </section>
      {metrics ? (
        <section>
          <h4>Metrics</h4>
          <dl className="stage-metrics">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{Array.isArray(value) ? value.join(", ") : String(value)}</dd>
              </div>
            ))}
          </dl>
        </section>
      ) : null}
    </article>
  );
}

export function StageToolkitView(): JSX.Element {
  const statusQuery = useStageStatusQuery();
  const initMutation = useStageInitMutation();

  const [selection, setSelection] = useState<StageAgentSelection>("both");

  const stageStatus = statusQuery.data;
  const initResult = initMutation.data;

  const stdout = initResult?.stdout?.trim();
  const stderr = initResult?.stderr?.trim();

  const mutationError = initMutation.error ? String(initMutation.error) : null;

  const currentAgentLabel = useMemo(
    () => AGENT_OPTIONS.find((option) => option.value === selection)?.label ?? "Claude + Codex",
    [selection],
  );

  const handleStageInit = () => {
    initMutation.mutate({ agents: selection });
  };

  return (
    <div className="stage-toolkit">
      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Stage-Aware project status</h2>
            <p>
              Check whether the key files for Claude Code and Codex CLI are present in the current
              workspace.
            </p>
          </div>
          <button
            className="secondary-btn"
            type="button"
            onClick={() => statusQuery.refetch()}
            disabled={statusQuery.isFetching}
          >
            {statusQuery.isFetching ? "Checking…" : "Check again"}
          </button>
        </header>

        {statusQuery.isLoading ? (
          <p className="stage-info">Loading status…</p>
        ) : statusQuery.isError ? (
          <p className="stage-error">
            Could not fetch status. {String(statusQuery.error)}
          </p>
        ) : (
          <div className="stage-status-grid">
            <AgentStatusCard title="Claude Code" status={stageStatus?.claude} />
            <AgentStatusCard title="Codex CLI" status={stageStatus?.codex} />
            <DocsStatusCard status={stageStatus?.docs} />
          </div>
        )}
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Ollama and recommendations</h2>
            <p>
              Ollama service configuration and the insight history now live on a dedicated page.
            </p>
          </div>
        </header>

        <article className="stage-card">
          <p>
            Visit the <Link to="/ollama">Ollama</Link> tab to start the server, test models, and
            manage automatically generated recommendations.
          </p>
          <p className="stage-hint">
            From there you can adjust the model and cadence, launch manual analyses, and review the
            latest insights.
          </p>
        </article>
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Initialize or reinstall instructions</h2>
            <p>
              Run <code>init_project.py --existing</code> (optionally add <code>--dry-run</code> to
              simulate) against the current workspace with the selected agents.
            </p>
          </div>
        </header>

        <div className="stage-actions">
          <label className="stage-radio-group-title" htmlFor="agent-selection">
            Agents
          </label>
          <div className="stage-radio-group" id="agent-selection">
            {AGENT_OPTIONS.map((option) => (
              <label key={option.value} className="stage-radio">
                <input
                  type="radio"
                  name="agent"
                  value={option.value}
                  checked={selection === option.value}
                  onChange={() => setSelection(option.value)}
                  disabled={initMutation.isPending}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
          <button
            className="primary-btn"
            type="button"
            onClick={handleStageInit}
            disabled={initMutation.isPending}
          >
            {initMutation.isPending ? "Running…" : `Initialize (${currentAgentLabel})`}
          </button>
        </div>

        {mutationError ? <p className="stage-error">{mutationError}</p> : null}
      </section>

      <section className="stage-section">
        {statusQuery.isLoading ? (
          <p className="stage-info">Calculating stage detection…</p>
        ) : stageStatus ? (
          <StageDetectionCard detection={stageStatus.detection} />
        ) : (
          <p className="stage-info">Unable to retrieve project status.</p>
        )}
      </section>

      {initResult ? (
        <section className="stage-section">
          <header className="stage-section-header">
            <div>
              <h2>init_project.py output</h2>
              <p>
                Command: <code>{initResult.command.join(" ")}</code>
              </p>
            </div>
          </header>
          {stdout ? (
            <pre className="stage-output">{stdout}</pre>
          ) : (
            <p className="stage-info">No stdout output.</p>
          )}
          {stderr ? <pre className="stage-output error">{stderr}</pre> : null}
        </section>
      ) : null}
    </div>
  );
}

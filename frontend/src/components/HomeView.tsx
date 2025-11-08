import { Link } from "react-router-dom";
import type { UseQueryResult } from "@tanstack/react-query";

import type { StageDetectionStatus, StatusPayload } from "../api/types";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";

function detectionBadgeLabel(detection?: StageDetectionStatus): string {
  if (!detection) {
    return "Loading detection…";
  }
  if (!detection.available) {
    return detection.error ?? "Detection unavailable";
  }
  const stage = detection.recommended_stage ?? "?";
  const confidence = detection.confidence ? detection.confidence.toUpperCase() : "NO CONF.";
  return `Stage ${stage} · ${confidence}`;
}

export function HomeView({
  statusQuery,
}: {
  statusQuery: UseQueryResult<StatusPayload>;
}): JSX.Element {
  const stageStatusQuery = useStageStatusQuery();

  const detection = stageStatusQuery.data?.detection;
  const detectionAvailable = detection?.available ?? false;

  const detectionTone = detectionAvailable ? "success" : "warn";
  const detectionLabel = detectionBadgeLabel(detection);
  const backendOffline =
    statusQuery.isError || (!statusQuery.isFetching && !statusQuery.data && !statusQuery.isLoading);
  const executableUrl = "https://github.com/jesusramos/Claude-Prompt-Library/releases/latest";

  return (
    <div className="home-view">
      {backendOffline && (
        <div className="home-alert home-alert--error" role="alert">
          <div className="home-alert__text">
            <strong>Backend desconectado.</strong>
            <span>
              Inicia el servidor local o descarga el ejecutable empaquetado para Code Map.
            </span>
          </div>
          <a
            className="home-alert__cta"
            href={executableUrl}
            target="_blank"
            rel="noreferrer"
          >
            Descargar ejecutable →
          </a>
        </div>
      )}
      <section className="home-hero">
        <div className="home-hero__glow" aria-hidden />
        <div className="home-hero__content">
          <span className={`home-stage-pill ${detectionTone}`}>
            {stageStatusQuery.isLoading ? "Calculating…" : detectionLabel}
          </span>
          <h2>Build with AI without losing control.</h2>
          <p>
            Keep agents aligned with project rules using the Stage Toolkit or explore code with the
            enriched Code Map.
          </p>
        </div>
      </section>

      <section className="home-card-grid">
        <Link to="/stage-toolkit" className="home-card">
          <div className="home-card-body">
            <h3>Project Stage Toolkit</h3>
            <p>
              Run <code>init_project.py</code>, validate the files required by Claude Code and Codex
              CLI, and review the detected project stage.
            </p>
          </div>
          <span className="home-card-cta">Open toolkit →</span>
        </Link>

        <Link to="/overview" className="home-card">
          <div className="home-card-body">
            <h3>Overview</h3>
            <p>
              Review detections, alerts, and recent activity from a single dashboard before diving
              deeper.
            </p>
          </div>
          <span className="home-card-cta">Open overview →</span>
        </Link>

        <Link to="/code-map" className="home-card">
          <div className="home-card-body">
            <h3>Code Map</h3>
            <p>
              Browse symbols, semantic search, and recent repository activity—ideal for exploring
              the code with context.
            </p>
          </div>
          <span className="home-card-cta">Open Code Map →</span>
        </Link>

        <Link to="/class-uml" className="home-card">
          <div className="home-card-body">
            <h3>Class UML</h3>
            <p>
              UML diagrams with class attributes and methods—perfect for understanding internals
              without extra noise.
            </p>
          </div>
          <span className="home-card-cta">View UML →</span>
        </Link>

        <Link to="/linters" className="home-card">
          <div className="home-card-body">
            <h3>Linters</h3>
            <p>
              Check configured linter status, latest results, and logs to maintain code quality.
            </p>
          </div>
          <span className="home-card-cta">View linters →</span>
        </Link>

        <Link to="/ollama" className="home-card">
          <div className="home-card-body">
            <h3>Ollama Insights</h3>
            <p>
              Configure models, generate insights, and monitor scheduled runs for automated guidance.
            </p>
          </div>
          <span className="home-card-cta">Open Ollama →</span>
        </Link>

        <Link to="/prompts" className="home-card">
          <div className="home-card-body">
            <h3>Prompts</h3>
            <p>
              Explore reusable prompt templates to guide agents and capture team best practices.
            </p>
          </div>
          <span className="home-card-cta">Open Prompts →</span>
        </Link>

        <Link to="/settings" className="home-card">
          <div className="home-card-body">
            <h3>Settings</h3>
            <p>
              Configure project paths, automation toggles, and integrations to match your workflow.
            </p>
          </div>
          <span className="home-card-cta">Open Settings →</span>
        </Link>
      </section>
    </div>
  );
}

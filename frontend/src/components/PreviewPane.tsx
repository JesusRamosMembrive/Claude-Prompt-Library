import { useQuery } from "@tanstack/react-query";

import { getPreview } from "../api/client";
import { queryKeys } from "../api/queryKeys";

interface PreviewPaneProps {
  path: string;
}

const HTML_MIME_RE = /html/i;
const TEXT_MIME_RE = /(text|json|xml)/i;

export function PreviewPane({ path }: PreviewPaneProps): JSX.Element | null {
  const previewQuery = useQuery({
    queryKey: queryKeys.preview(path),
    queryFn: () => getPreview(path),
    enabled: Boolean(path),
  });

  if (!path) {
    return null;
  }

  if (previewQuery.isLoading) {
    return <p style={{ color: "#7f869d", fontSize: "13px" }}>Cargando vista previa…</p>;
  }

  if (previewQuery.isError) {
    return (
      <div className="error-banner">
        No se pudo cargar la previsualización: {String(previewQuery.error)}
      </div>
    );
  }

  const content = previewQuery.data?.content ?? "";
  const contentType = previewQuery.data?.contentType ?? "";
  const isHtml = HTML_MIME_RE.test(contentType);
  const isTextual = TEXT_MIME_RE.test(contentType);

  if (isHtml) {
    return (
      <iframe
        className="preview-frame"
        sandbox="allow-scripts allow-same-origin"
        srcDoc={content}
        title={`Vista previa de ${path}`}
      />
    );
  }

  if (isTextual) {
    return (
      <pre className="preview-plain" data-testid="preview-plain">
        {content}
      </pre>
    );
  }

  return (
    <p className="preview-fallback">
      No hay previsualización disponible para este tipo de archivo ({contentType || "desconocido"}).
    </p>
  );
}

interface DocstringsSectionProps {
  includeDocstrings: boolean;
  disabled: boolean;
  onToggleDocstrings: (value: boolean) => void;
}

export function DocstringsSection({
  includeDocstrings,
  disabled,
  onToggleDocstrings,
}: DocstringsSectionProps): JSX.Element {
  return (
    <section className="settings-card">
      <h2>Visualización</h2>
      <p>Ajusta cómo se muestran los símbolos en la interfaz.</p>
      <div className="setting-row">
        <div className="setting-info">
          <strong>Modo de símbolos</strong>
          <span>Agrupación principal para el explorador.</span>
        </div>
        <div className="setting-controls">
          <select value="tree" disabled>
            <option value="tree">Carpeta → archivo → símbolo</option>
          </select>
        </div>
      </div>
      <div className="toggle-row">
        <div>
          <strong>Mostrar docstrings</strong>
          <span>
            Controla si el analizador extrae docstrings para mostrarlos en la UI.
          </span>
        </div>
        <input
          type="checkbox"
          checked={includeDocstrings}
          onChange={(event) => onToggleDocstrings(event.target.checked)}
          disabled={disabled}
        />
      </div>
      <div className="toggle-row">
        <div>
          <strong>Tema oscuro</strong>
          <span>Activa la paleta actual del workspace.</span>
        </div>
        <input type="checkbox" checked readOnly />
      </div>
    </section>
  );
}

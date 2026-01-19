import { css } from 'lit';

export const sharedStyles = css`
  :host {
    display: block;
    --tt-primary-color: var(--primary-color, #03a9f4);
    --tt-accent-color: var(--accent-color, #ff9800);
    --tt-card-background: var(--card-background-color, #fff);
    --tt-primary-text: var(--primary-text-color, #212121);
    --tt-secondary-text: var(--secondary-text-color, #727272);
    --tt-divider-color: var(--divider-color, rgba(0, 0, 0, 0.12));
    --tt-border-radius: var(--ha-card-border-radius, 12px);
    --tt-spacing: 16px;
  }

  ha-card {
    padding: var(--tt-spacing);
    background: var(--tt-card-background);
    border-radius: var(--tt-border-radius);
  }

  /* Tab Bar */
  .tab-bar {
    display: flex;
    border-bottom: 2px solid var(--tt-divider-color);
    margin-bottom: var(--tt-spacing);
  }

  .tab {
    flex: 1;
    padding: 12px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    color: var(--tt-secondary-text);
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
    user-select: none;
  }

  .tab:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .tab.active {
    color: var(--tt-primary-color);
    border-bottom-color: var(--tt-primary-color);
  }

  /* Form Elements */
  .form-group {
    margin-bottom: var(--tt-spacing);
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--tt-primary-text);
  }

  select,
  input[type="range"] {
    width: 100%;
    padding: 10px;
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: var(--tt-card-background);
    color: var(--tt-primary-text);
    font-size: 14px;
  }

  select:focus,
  input:focus {
    outline: none;
    border-color: var(--tt-primary-color);
  }

  /* Buttons */
  .button-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    background: var(--tt-primary-color);
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
  }

  button:hover {
    filter: brightness(110%);
    transform: translateY(-1px);
  }

  button:active {
    transform: translateY(0);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  button.secondary {
    background: var(--tt-secondary-text);
  }

  button.accent {
    background: var(--tt-accent-color);
  }

  button.danger {
    background: #f44336;
  }

  /* Control Panel */
  .control-panel {
    padding: var(--tt-spacing);
    border: 1px solid var(--tt-divider-color);
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.02);
  }

  /* Slider Container */
  .slider-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  input[type="range"] {
    flex: 1;
  }

  .slider-value {
    min-width: 50px;
    text-align: center;
    font-weight: 500;
    color: var(--tt-primary-text);
  }

  /* Result Box */
  .result-box {
    margin-top: var(--tt-spacing);
    padding: 12px;
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.02);
    min-height: 50px;
    color: var(--tt-primary-text);
  }

  .result-box.success {
    border-color: #4caf50;
    background: rgba(76, 175, 80, 0.1);
  }

  .result-box.error {
    border-color: #f44336;
    background: rgba(244, 67, 54, 0.1);
  }

  /* Event Log */
  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .log-controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .log-container {
    border: 1px solid var(--tt-divider-color);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.02);
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .log-table {
    width: 100%;
    border-collapse: collapse;
  }

  .log-table th {
    position: sticky;
    top: 0;
    background: var(--tt-card-background);
    padding: 8px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--tt-divider-color);
    color: var(--tt-primary-text);
  }

  .log-table td {
    padding: 6px 8px;
    border-bottom: 1px solid var(--tt-divider-color);
    color: var(--tt-secondary-text);
  }

  .log-table tr:hover {
    background: rgba(0, 0, 0, 0.03);
  }

  .log-empty {
    padding: 20px;
    text-align: center;
    color: var(--tt-secondary-text);
  }

  /* Status Footer */
  .status-footer {
    margin-top: var(--tt-spacing);
    padding-top: var(--tt-spacing);
    border-top: 1px solid var(--tt-divider-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    color: var(--tt-secondary-text);
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #9e9e9e;
  }

  .status-dot.connected {
    background: #4caf50;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  /* Responsive */
  @media (max-width: 600px) {
    .button-group {
      flex-direction: column;
    }

    button {
      width: 100%;
    }

    .tab {
      padding: 10px 6px;
      font-size: 14px;
    }
  }

  /* Checkbox */
  .checkbox-container {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  input[type="checkbox"] {
    width: auto;
    cursor: pointer;
  }
`;

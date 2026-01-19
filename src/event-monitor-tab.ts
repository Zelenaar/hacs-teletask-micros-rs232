import { LitElement, html, TemplateResult } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, TeletaskTestCardConfig, TeletaskEvent, LogEntry, FUNCTION_CODES } from './types';
import { sharedStyles } from './styles';

/**
 * Event Monitor Tab Component
 *
 * Displays real-time TeleTask communication events:
 * - Subscribes to 'teletask_state_updated' events
 * - Shows timestamp, type, function, device number, and state
 * - Auto-scroll to latest events
 * - Clear log functionality
 * - Connection status indicator
 */
@customElement('event-monitor-tab')
export class EventMonitorTab extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ attribute: false }) public config!: TeletaskTestCardConfig;

  @state() private _events: LogEntry[] = [];
  @state() private _autoScroll: boolean = true;
  @state() private _isConnected: boolean = false;
  private _unsubscribe?: () => void;

  static styles = sharedStyles;

  /**
   * Subscribe to TeleTask events when component is added to DOM
   */
  connectedCallback(): void {
    super.connectedCallback();
    this._subscribeToEvents();
    this._checkConnection();
  }

  /**
   * Unsubscribe from events when component is removed from DOM
   */
  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this._unsubscribe) {
      this._unsubscribe();
    }
  }

  /**
   * Subscribe to TeleTask state update events
   */
  private async _subscribeToEvents(): Promise<void> {
    try {
      this._unsubscribe = await this.hass.connection.subscribeEvents(
        (event: TeletaskEvent) => this._handleEvent(event),
        'teletask_state_updated'
      );
      console.log('Subscribed to teletask_state_updated events');
    } catch (err) {
      console.error('Failed to subscribe to TeleTask events:', err);
    }
  }

  /**
   * Check if TeleTask hub is connected
   */
  private _checkConnection(): void {
    // Look for any TeleTask entity to determine if integration is running
    if (this.hass && this.hass.states) {
      const teletaskEntities = Object.keys(this.hass.states).filter((id) => id.includes('teletask'));
      this._isConnected = teletaskEntities.length > 0;
    }
  }

  /**
   * Handle incoming TeleTask event
   */
  private _handleEvent(event: TeletaskEvent): void {
    const timestamp = new Date().toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    const logEntry: LogEntry = {
      timestamp,
      type: 'EVENT',
      func: this._decodeFunctionName(event.data.func),
      num: event.data.num.toString(),
      state: this._formatState(event.data.state, event.data.func),
    };

    // Add to events list
    this._events = [...this._events, logEntry];

    // Limit to max events
    const maxEvents = this.config.max_events || 100;
    if (this._events.length > maxEvents) {
      this._events = this._events.slice(-maxEvents);
    }

    // Auto-scroll to bottom
    if (this._autoScroll) {
      this._scrollToBottom();
    }
  }

  /**
   * Decode function code to readable name
   */
  private _decodeFunctionName(funcCode: number): string {
    return FUNCTION_CODES[funcCode] || `UNKNOWN(${funcCode})`;
  }

  /**
   * Format state value based on function type
   */
  private _formatState(state: number, funcCode: number): string {
    // For relays and flags: 0 = OFF, 255 = ON
    if (funcCode === 1 || funcCode === 15) {
      return state === 0 ? 'OFF' : state === 255 ? 'ON' : `${state}`;
    }

    // For dimmers: show brightness value (0-255)
    if (funcCode === 2) {
      return `${state}`;
    }

    // For moods: 0 = OFF, 255 = ON
    if (funcCode === 8 || funcCode === 9 || funcCode === 10) {
      return state === 0 ? 'OFF' : state === 255 ? 'ON' : `${state}`;
    }

    // For sensors: show raw value
    if (funcCode === 20 || funcCode === 21) {
      return `${state}`;
    }

    return `${state}`;
  }

  /**
   * Scroll log container to bottom
   */
  private _scrollToBottom(): void {
    requestAnimationFrame(() => {
      const container = this.shadowRoot?.querySelector('.log-container');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });
  }

  /**
   * Handle clear log button
   */
  private _handleClearLog(): void {
    this._events = [];
  }

  /**
   * Handle auto-scroll checkbox
   */
  private _handleAutoScrollToggle(e: Event): void {
    this._autoScroll = (e.target as HTMLInputElement).checked;
  }

  /**
   * Render log header with controls
   */
  private _renderLogHeader(): TemplateResult {
    return html`
      <div class="log-header">
        <h3 style="margin: 0; color: var(--tt-primary-text);">TeleTask Communication Log</h3>
        <div class="log-controls">
          <div class="checkbox-container">
            <input
              type="checkbox"
              id="auto-scroll"
              ?checked=${this._autoScroll}
              @change=${this._handleAutoScrollToggle}
            />
            <label for="auto-scroll" style="margin: 0; cursor: pointer;">Auto-scroll</label>
          </div>
          <button @click=${this._handleClearLog} class="secondary">Clear Log</button>
        </div>
      </div>
    `;
  }

  /**
   * Render event log table
   */
  private _renderLogTable(): TemplateResult {
    if (this._events.length === 0) {
      return html`
        <div class="log-container">
          <div class="log-empty">No events yet. Trigger a device to see communication logs.</div>
        </div>
      `;
    }

    return html`
      <div class="log-container">
        <table class="log-table">
          <thead>
            <tr>
              <th>TIME</th>
              <th>TYPE</th>
              <th>FUNC</th>
              <th>NUM</th>
              <th>STATE</th>
            </tr>
          </thead>
          <tbody>
            ${this._events.map(
              (entry) => html`
                <tr>
                  <td>${entry.timestamp}</td>
                  <td>${entry.type}</td>
                  <td>${entry.func}</td>
                  <td>${entry.num}</td>
                  <td>${entry.state}</td>
                </tr>
              `
            )}
          </tbody>
        </table>
      </div>
    `;
  }

  /**
   * Render status footer
   */
  private _renderStatusFooter(): TemplateResult {
    return html`
      <div class="status-footer">
        <div>Events: ${this._events.length}</div>
        <div class="status-indicator">
          <span>Connection:</span>
          <div class="status-dot ${this._isConnected ? 'connected' : ''}"></div>
          <span>${this._isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
    `;
  }

  /**
   * Update connection status when hass changes
   */
  protected updated(changedProperties: Map<string, any>): void {
    if (changedProperties.has('hass')) {
      this._checkConnection();
    }
  }

  /**
   * Render the tab content
   */
  protected render(): TemplateResult {
    return html`
      <div class="event-monitor">
        ${this._renderLogHeader()} ${this._renderLogTable()} ${this._renderStatusFooter()}
      </div>
    `;
  }
}

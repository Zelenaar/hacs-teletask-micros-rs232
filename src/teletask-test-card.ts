import { LitElement, html, TemplateResult } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, TeletaskTestCardConfig, TabName } from './types';
import { sharedStyles } from './styles';
import './device-control-tab';
import './event-monitor-tab';

/**
 * TeleTask Test Card
 *
 * Custom Lovelace card for testing TeleTask MICROS devices and monitoring events.
 *
 * @element teletask-test-card
 */
@customElement('teletask-test-card')
export class TeletaskTestCard extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private _config?: TeletaskTestCardConfig;
  @state() private _activeTab: TabName = 'devices';

  static styles = sharedStyles;

  /**
   * Set the card configuration
   */
  public setConfig(config: TeletaskTestCardConfig): void {
    if (!config) {
      throw new Error('Invalid configuration');
    }

    // Migrate old 'mood' type to new separate mood types (backward compatibility)
    let deviceTypes = config.show_device_types || ['relay', 'dimmer', 'local_mood', 'general_mood', 'timed_mood', 'flag'];

    // @ts-ignore - Allow 'mood' for backward compatibility
    if (deviceTypes.includes('mood')) {
      // Replace 'mood' with the three new mood types
      deviceTypes = deviceTypes
        // @ts-ignore
        .filter(type => type !== 'mood')
        .concat(['local_mood', 'general_mood', 'timed_mood']);
    }

    this._config = {
      type: 'custom:teletask-test-card',
      default_tab: config.default_tab || 'devices',
      show_device_types: deviceTypes,
      max_events: config.max_events || 100,
      ...config,
    };

    this._activeTab = this._config.default_tab || 'devices';
  }

  /**
   * Return stub config for card picker
   */
  public static getStubConfig() {
    return {
      type: 'custom:teletask-test-card',
      default_tab: 'devices',
    };
  }

  /**
   * Get card size for layout calculations (Lovelace uses this)
   */
  public getCardSize(): number {
    return 6;
  }

  /**
   * Handle tab switching
   */
  private _handleTabClick(tab: TabName): void {
    this._activeTab = tab;
  }

  /**
   * Render the card
   */
  protected render(): TemplateResult {
    if (!this._config || !this.hass) {
      return html`
        <ha-card>
          <div style="padding: 16px;">
            Loading TeleTask Test Card...
          </div>
        </ha-card>
      `;
    }

    return html`
      <ha-card>
        <div class="tab-bar">
          <div
            class="tab ${this._activeTab === 'devices' ? 'active' : ''}"
            @click=${() => this._handleTabClick('devices')}
          >
            Devices
          </div>
          <div
            class="tab ${this._activeTab === 'events' ? 'active' : ''}"
            @click=${() => this._handleTabClick('events')}
          >
            Events
          </div>
        </div>

        <div class="tab-content">
          ${this._activeTab === 'devices'
            ? html`
                <device-control-tab
                  .hass=${this.hass}
                  .config=${this._config}
                ></device-control-tab>
              `
            : html`
                <event-monitor-tab
                  .hass=${this.hass}
                  .config=${this._config}
                ></event-monitor-tab>
              `}
        </div>
      </ha-card>
    `;
  }
}

// Register the card with the card picker
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: 'teletask-test-card',
  name: 'TeleTask Test Card',
  description: 'Test TeleTask MICROS devices and monitor communication events in real-time.',
  preview: false,
  documentationURL: 'https://github.com/Zelenaar/hacs-teletask-micros-rs232',
});

console.info(
  '%c TELETASK-TEST-CARD %c v1.9.8 ',
  'background-color: #03a9f4; color: #fff; font-weight: bold;',
  'background-color: #333; color: #fff; font-weight: bold;'
);

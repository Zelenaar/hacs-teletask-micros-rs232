import { LitElement, html, TemplateResult } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, TeletaskTestCardConfig, DeviceType, TeletaskDevice, MoodType } from './types';
import { sharedStyles } from './styles';

/**
 * Device Control Tab Component
 *
 * Provides controls for testing TeleTask devices:
 * - Relays: ON/OFF/TOGGLE/GET
 * - Dimmers: Slider + SET/TOGGLE/GET
 * - Moods: Type selector + ON/OFF/TOGGLE/GET
 * - Flags: ON/OFF/TOGGLE/GET
 */
@customElement('device-control-tab')
export class DeviceControlTab extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ attribute: false }) public config!: TeletaskTestCardConfig;

  @state() private _selectedType: DeviceType = 'relay';
  @state() private _selectedRoom: string = 'all';
  @state() private _selectedDevice?: TeletaskDevice;
  @state() private _dimmerValue: number = 128;
  @state() private _result: string = '';
  @state() private _resultType: 'success' | 'error' | '' = '';

  static styles = sharedStyles;

  /**
   * Extract TeleTask devices from Home Assistant entity registry
   */
  private _getDevicesByType(type: DeviceType): TeletaskDevice[] {
    if (!this.hass) return [];

    const devicesByNumber = new Map<number, TeletaskDevice>();  // Deduplicate by device number
    const entities = Object.values(this.hass.states);

    for (const entity of entities) {
      // Check if entity belongs to TeleTask integration
      if (!entity.entity_id.includes('teletask')) continue;

      const attrs = entity.attributes;
      // Add null check for attributes
      if (!attrs) continue;

      // Skip if no device number
      if (!attrs.teletask_number) continue;

      let deviceType: DeviceType | null = null;
      let domain = entity.entity_id.split('.')[0];

      // Determine device type from domain and teletask_function attribute
      if (type === 'relay') {
        if ((domain === 'light' || domain === 'switch') && attrs.teletask_function === 1) {
          deviceType = 'relay';
        }
      } else if (type === 'dimmer') {
        // Only show light entities for dimmers, not number entities
        if (domain === 'light' && attrs.teletask_function === 2) {
          deviceType = 'dimmer';
        }
      } else if (type === 'local_mood') {
        if (domain === 'button' && attrs.teletask_function === 8) {
          deviceType = 'local_mood';
        }
      } else if (type === 'general_mood') {
        if (domain === 'button' && attrs.teletask_function === 9) {
          deviceType = 'general_mood';
        }
      } else if (type === 'timed_mood') {
        if (domain === 'button' && attrs.teletask_function === 10) {
          deviceType = 'timed_mood';
        }
      } else if (type === 'flag') {
        if (domain === 'binary_sensor' && attrs.teletask_function === 15) {
          deviceType = 'flag';
        }
      }

      if (deviceType) {
        const deviceNum = attrs.teletask_number;
        const device: TeletaskDevice = {
          entity_id: entity.entity_id,
          number: deviceNum,
          room: attrs.room || 'Unknown',
          name: attrs.friendly_name || entity.entity_id,
          type: deviceType,
          domain: domain,
        };

        // Deduplicate by device number - prefer light over switch for relays
        if (!devicesByNumber.has(deviceNum)) {
          devicesByNumber.set(deviceNum, device);
        } else {
          const existing = devicesByNumber.get(deviceNum)!;
          // Prefer light domain over switch for relays
          if (type === 'relay' && domain === 'light' && existing.domain === 'switch') {
            devicesByNumber.set(deviceNum, device);
          }
        }
      }
    }

    return Array.from(devicesByNumber.values()).sort((a, b) => a.number - b.number);
  }

  /**
   * Get unique rooms from devices
   */
  private _getRooms(): string[] {
    const devices = this._getDevicesByType(this._selectedType);
    const rooms = new Set<string>();

    for (const device of devices) {
      if (device.room && device.room !== 'Unknown') {
        rooms.add(device.room);
      }
    }

    return Array.from(rooms).sort();
  }

  /**
   * Get filtered devices by room selection
   */
  private _getFilteredDevices(): TeletaskDevice[] {
    const devices = this._getDevicesByType(this._selectedType);

    if (this._selectedRoom === 'all') {
      return devices;
    }

    return devices.filter(device => device.room === this._selectedRoom);
  }

  /**
   * Handle device type selection
   */
  private _handleTypeChange(e: Event): void {
    const select = e.target as HTMLSelectElement;
    this._selectedType = select.value as DeviceType;
    this._selectedRoom = 'all';  // Reset room filter
    this._selectedDevice = undefined;
    this._result = '';
    this._resultType = '';
  }

  /**
   * Handle room filter selection
   */
  private _handleRoomChange(e: Event): void {
    const select = e.target as HTMLSelectElement;
    this._selectedRoom = select.value;
    this._selectedDevice = undefined;  // Reset device selection
    this._result = '';
    this._resultType = '';
  }

  /**
   * Handle device selection
   */
  private _handleDeviceChange(e: Event): void {
    const select = e.target as HTMLSelectElement;
    const devices = this._getFilteredDevices();
    this._selectedDevice = devices.find((d) => d.entity_id === select.value);
    this._result = '';
    this._resultType = '';

    // Set dimmer value to current brightness if applicable
    if (this._selectedDevice && this._selectedType === 'dimmer') {
      const state = this.hass.states[this._selectedDevice.entity_id];
      if (state && state.attributes.brightness) {
        this._dimmerValue = state.attributes.brightness;
      }
    }
  }

  /**
   * Handle relay/flag ON/OFF/TOGGLE actions
   */
  private async _handleRelayAction(action: 'on' | 'off' | 'toggle'): Promise<void> {
    if (!this._selectedDevice) return;

    try {
      const domain = this._selectedDevice.domain;
      const service = action === 'toggle' ? 'toggle' : `turn_${action}`;

      await this.hass.callService(domain, service, {
        entity_id: this._selectedDevice.entity_id,
      });

      this._result = `${this._selectedDevice.name}: ${action.toUpperCase()} command sent`;
      this._resultType = 'success';
    } catch (err) {
      this._result = `Error: ${err}`;
      this._resultType = 'error';
    }
  }

  /**
   * Handle dimmer SET action
   */
  private async _handleDimmerSet(): Promise<void> {
    if (!this._selectedDevice) return;

    try {
      await this.hass.callService('light', 'turn_on', {
        entity_id: this._selectedDevice.entity_id,
        brightness: this._dimmerValue,
      });

      this._result = `${this._selectedDevice.name}: Set to ${this._dimmerValue}`;
      this._resultType = 'success';
    } catch (err) {
      this._result = `Error: ${err}`;
      this._resultType = 'error';
    }
  }

  /**
   * Handle mood action
   */
  private async _handleMoodAction(action: 'on' | 'off' | 'toggle'): Promise<void> {
    if (!this._selectedDevice) return;

    try {
      // Determine mood type from device type
      const moodTypeMap: Record<string, MoodType> = {
        local_mood: 'LOCAL',
        general_mood: 'GENERAL',
        timed_mood: 'TIMED',
      };
      const moodType = moodTypeMap[this._selectedType] || 'LOCAL';

      // Moods use the teletask.set_mood service with string state values
      const state = action === 'on' ? 'ON' : action === 'off' ? 'OFF' : 'TOGGLE';

      await this.hass.callService('teletask', 'set_mood', {
        number: this._selectedDevice.number,
        type: moodType,
        state: state,
      });

      this._result = `${this._selectedDevice.name} (${moodType}): ${action.toUpperCase()}`;
      this._resultType = 'success';
    } catch (err) {
      this._result = `Error: ${err}`;
      this._resultType = 'error';
    }
  }

  /**
   * Handle GET STATUS action
   */
  private _handleGetStatus(): void {
    if (!this._selectedDevice) return;

    try {
      const state = this.hass.states[this._selectedDevice.entity_id];
      if (state) {
        let statusText = `${this._selectedDevice.name}: ${state.state.toUpperCase()}`;

        if (this._selectedType === 'dimmer' && state.attributes.brightness !== undefined) {
          statusText += ` (Brightness: ${state.attributes.brightness})`;
        }

        this._result = statusText;
        this._resultType = 'success';
      } else {
        this._result = 'Device state not available';
        this._resultType = 'error';
      }
    } catch (err) {
      this._result = `Error: ${err}`;
      this._resultType = 'error';
    }
  }

  /**
   * Get friendly display name for device type
   */
  private _getTypeDisplayName(type: DeviceType): string {
    const typeNames: Record<DeviceType, string> = {
      relay: 'Relay',
      dimmer: 'Dimmer',
      local_mood: 'Local Mood',
      general_mood: 'General Mood',
      timed_mood: 'Timed Mood',
      flag: 'Flag',
    };
    return typeNames[type] || type;
  }

  /**
   * Render device type selector
   */
  private _renderTypeSelector(): TemplateResult {
    const types = this.config.show_device_types || ['relay', 'dimmer', 'local_mood', 'general_mood', 'timed_mood', 'flag'];

    return html`
      <div class="form-group">
        <label>Device Type:</label>
        <select @change=${this._handleTypeChange} .value=${this._selectedType}>
          ${types.map(
            (type) => html`
              <option value=${type} ?selected=${type === this._selectedType}>
                ${this._getTypeDisplayName(type)}
              </option>
            `
          )}
        </select>
      </div>
    `;
  }

  /**
   * Render room filter selector
   */
  private _renderRoomFilter(): TemplateResult {
    const rooms = this._getRooms();

    if (rooms.length === 0) {
      return html``;
    }

    return html`
      <div class="form-group">
        <label>Filter by Room:</label>
        <select @change=${this._handleRoomChange} .value=${this._selectedRoom}>
          <option value="all" ?selected=${this._selectedRoom === 'all'}>All Rooms</option>
          ${rooms.map(
            (room) => html`
              <option value=${room} ?selected=${this._selectedRoom === room}>
                ${room}
              </option>
            `
          )}
        </select>
      </div>
    `;
  }

  /**
   * Render device selector
   */
  private _renderDeviceSelector(): TemplateResult {
    const devices = this._getFilteredDevices();

    if (devices.length === 0) {
      const allDevices = this._getDevicesByType(this._selectedType);

      if (allDevices.length === 0) {
        return html`
          <div class="form-group">
            <label>Select Device:</label>
            <div style="padding: 12px; color: var(--tt-secondary-text);">
              No ${this._getTypeDisplayName(this._selectedType)} devices configured in TeleTask integration.
            </div>
          </div>
        `;
      } else {
        return html`
          <div class="form-group">
            <label>Select Device:</label>
            <div style="padding: 12px; color: var(--tt-secondary-text);">
              No ${this._getTypeDisplayName(this._selectedType)} devices in selected room.
            </div>
          </div>
        `;
      }
    }

    return html`
      <div class="form-group">
        <label>Select Device:</label>
        <select @change=${this._handleDeviceChange}>
          <option value="" ?selected=${!this._selectedDevice}>Select a device...</option>
          ${devices.map(
            (device) => html`
              <option value=${device.entity_id} ?selected=${this._selectedDevice?.entity_id === device.entity_id}>
                [${device.number}] ${device.room} - ${device.name}
              </option>
            `
          )}
        </select>
      </div>
    `;
  }

  /**
   * Render control panel based on device type
   */
  private _renderControlPanel(): TemplateResult {
    if (!this._selectedDevice) {
      return html`<div class="control-panel">Select a device to control</div>`;
    }

    // Relay and Flag controls (ON/OFF/TOGGLE)
    if (this._selectedType === 'relay' || this._selectedType === 'flag') {
      return html`
        <div class="control-panel">
          <div class="button-group">
            <button @click=${() => this._handleRelayAction('on')}>ON</button>
            <button @click=${() => this._handleRelayAction('off')} class="secondary">OFF</button>
            <button @click=${() => this._handleRelayAction('toggle')} class="accent">TOGGLE</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `;
    }

    // Dimmer controls (Slider + SET/TOGGLE)
    if (this._selectedType === 'dimmer') {
      return html`
        <div class="control-panel">
          <div class="slider-container">
            <label style="margin: 0;">Brightness:</label>
            <input
              type="range"
              min="0"
              max="255"
              .value=${String(this._dimmerValue)}
              @input=${(e: Event) => {
                this._dimmerValue = parseInt((e.target as HTMLInputElement).value);
              }}
            />
            <span class="slider-value">${this._dimmerValue}</span>
          </div>
          <div class="button-group">
            <button @click=${this._handleDimmerSet}>Set Dimmer</button>
            <button @click=${() => this._handleRelayAction('toggle')} class="accent">Toggle</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `;
    }

    // Mood controls (ON/OFF/TOGGLE for all mood types)
    if (this._selectedType === 'local_mood' || this._selectedType === 'general_mood' || this._selectedType === 'timed_mood') {
      return html`
        <div class="control-panel">
          <div class="button-group">
            <button @click=${() => this._handleMoodAction('on')}>ON</button>
            <button @click=${() => this._handleMoodAction('off')} class="secondary">OFF</button>
            <button @click=${() => this._handleMoodAction('toggle')} class="accent">TOGGLE</button>
          </div>
          <div style="margin-top: 12px;">
            <button @click=${this._handleGetStatus} style="width: 100%;">Get Status</button>
          </div>
        </div>
      `;
    }

    return html`<div class="control-panel">Unsupported device type</div>`;
  }

  /**
   * Render result box
   */
  private _renderResult(): TemplateResult {
    if (!this._result) {
      return html`<div class="result-box">Results will appear here...</div>`;
    }

    return html`<div class="result-box ${this._resultType}">${this._result}</div>`;
  }

  /**
   * Render the tab content
   */
  protected render(): TemplateResult {
    return html`
      <div class="device-control">
        ${this._renderTypeSelector()}
        ${this._renderRoomFilter()}
        ${this._renderDeviceSelector()}
        ${this._renderControlPanel()}

        <div style="margin-top: var(--tt-spacing);">
          <label>Last Result:</label>
          ${this._renderResult()}
        </div>
      </div>
    `;
  }
}

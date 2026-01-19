/**
 * TypeScript type definitions for TeleTask Test Card
 */

// Home Assistant types
export interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  config: any;
  themes: any;
  language: string;
  callService: (domain: string, service: string, data?: any) => Promise<any>;
  callWS: (request: any) => Promise<any>;
  connection: Connection;
}

export interface Connection {
  subscribeEvents: (callback: (event: any) => void, eventType?: string) => Promise<() => void>;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: { [key: string]: any };
  last_changed: string;
  last_updated: string;
  context: any;
}

// Card configuration
export interface TeletaskTestCardConfig {
  type: string;
  default_tab?: 'devices' | 'events';
  show_device_types?: DeviceType[];
  max_events?: number;
}

// Device types
export type DeviceType = 'relay' | 'dimmer' | 'mood' | 'flag';

export interface TeletaskDevice {
  entity_id: string;
  number: number;
  room: string;
  name: string;
  type: DeviceType;
  domain: string;
}

// Event types
export interface TeletaskEvent {
  event_type: string;
  data: {
    func: number;
    num: number;
    state: number;
    timestamp?: string;
  };
  time_fired: string;
}

export interface LogEntry {
  timestamp: string;
  type: string;
  func: string;
  num: string;
  state: string;
}

// Function code mapping
export const FUNCTION_CODES: { [key: number]: string } = {
  1: 'RELAY',
  2: 'DIMMER',
  8: 'LOCMOOD',
  9: 'GENMOOD',
  10: 'TIMEDMOOD',
  15: 'FLAG',
  20: 'SENSOR',
  21: 'INPUT',
};

// Mood types
export type MoodType = 'LOCAL' | 'GENERAL' | 'TIMED';

// Tab names
export type TabName = 'devices' | 'events';

// EventBus.js - Decoupled Pub/Sub Event Dispatcher
export class EventBus {
  constructor() {
    this.events = new Map();
  }

  on(event, callback) {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event).push(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    if (!this.events.has(event)) return;
    const callbacks = this.events.get(event).filter((cb) => cb !== callback);
    this.events.set(event, callbacks);
  }

  emit(event, payload = null) {
    if (!this.events.has(event)) return;
    this.events.get(event).forEach((cb) => {
      try {
        cb(payload);
      } catch (err) {
        console.error(`[EventBus] Error in handler for event '${event}':`, err);
      }
    });
  }
}

export const eventBus = new EventBus();

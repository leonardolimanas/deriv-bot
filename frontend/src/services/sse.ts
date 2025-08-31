export class SSEService {
  private eventSource: EventSource | null = null;
  private listeners: Map<string, (data: any) => void> = new Map();

  connect(url: string = '/api/ticks/stream') {
    if (this.eventSource) {
      this.disconnect();
    }

    // Connecting to SSE
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      // SSE connection opened successfully
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Notify listeners
        if (this.listeners.has(data.type)) {
          this.listeners.get(data.type)!(data.data);
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('❌ SSE connection error:', error);
      console.error('❌ Error details:', {
        type: error.type,
        target: error.target,
        readyState: this.eventSource?.readyState,
        url: this.eventSource?.url
      });
      this.reconnect();
    };


  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  reconnect() {
            // Reconnecting SSE...
    setTimeout(() => {
      this.connect();
    }, 1000);
  }

  on(event: string, callback: (data: any) => void) {
    this.listeners.set(event, callback);
  }

  off(event: string) {
    this.listeners.delete(event);
  }
}

export const sseService = new SSEService();

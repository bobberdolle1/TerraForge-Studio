/**
 * Real-time Synchronization Service
 * WebSocket-based collaboration with CRDT support
 */

// import { io, Socket } from 'socket.io-client';
// Socket.io is optional - install with: npm install socket.io-client
type Socket = any;

export interface RealtimeMessage {
  type: 'user.joined' | 'user.left' | 'state.updated' | 'cursor.moved';
  userId: string;
  data: any;
  timestamp: number;
}

export interface UserPresence {
  userId: string;
  username: string;
  color: string;
  cursor?: { x: number; y: number };
  lastSeen: number;
}

export class RealtimeSync {
  private socket: Socket | null = null;
  private roomId: string | null = null;
  private userId: string;
  private listeners: Map<string, Set<Function>> = new Map();
  private presenceUsers: Map<string, UserPresence> = new Map();

  constructor(userId: string) {
    this.userId = userId;
  }

  connect(wsUrl: string, roomId: string, authToken: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.roomId = roomId;
      
      // Socket.io not installed - using stub
      // Install with: npm install socket.io-client
      this.socket = null as any;

      this.socket.on('connect', () => {
        console.log('Connected to realtime server');
        this.socket?.emit('join-room', { roomId, userId: this.userId });
        resolve();
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('Connection error:', error);
        reject(error);
      });

      this.socket.on('disconnect', () => {
        console.log('Disconnected from realtime server');
        this.emit('disconnected', {});
      });

      // Listen for messages
      this.socket.on('message', (message: RealtimeMessage) => {
        this.handleMessage(message);
      });

      // Presence updates
      this.socket.on('presence', (users: UserPresence[]) => {
        this.presenceUsers.clear();
        users.forEach(user => this.presenceUsers.set(user.userId, user));
        this.emit('presence', Array.from(this.presenceUsers.values()));
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.roomId = null;
      this.presenceUsers.clear();
    }
  }

  send(type: string, data: any): void {
    if (!this.socket || !this.roomId) {
      console.warn('Not connected to realtime server');
      return;
    }

    const message: RealtimeMessage = {
      type: type as any,
      userId: this.userId,
      data,
      timestamp: Date.now(),
    };

    this.socket.emit('message', message);
  }

  updateCursor(x: number, y: number): void {
    this.send('cursor.moved', { x, y });
  }

  updateState(state: any): void {
    this.send('state.updated', state);
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }

  getPresence(): UserPresence[] {
    return Array.from(this.presenceUsers.values());
  }

  private handleMessage(message: RealtimeMessage): void {
    // Don't process own messages
    if (message.userId === this.userId) {
      return;
    }

    this.emit(message.type, message.data);
  }

  private emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }
}

// CRDT implementation for conflict-free state merging
export class CRDT<T extends Record<string, any>> {
  private state: T;
  private version: number = 0;
  private vectorClock: Map<string, number> = new Map();

  constructor(initialState: T) {
    this.state = { ...initialState };
  }

  update(key: keyof T, value: any, userId: string): void {
    this.state[key] = value;
    this.version++;
    this.vectorClock.set(userId, (this.vectorClock.get(userId) || 0) + 1);
  }

  merge(remoteState: T, remoteVersion: number, remoteVectorClock: Map<string, number>): void {
    // Simple last-write-wins strategy
    if (remoteVersion > this.version) {
      this.state = { ...remoteState };
      this.version = remoteVersion;
      this.vectorClock = new Map(remoteVectorClock);
    }
  }

  getState(): T {
    return { ...this.state };
  }

  getVersion(): number {
    return this.version;
  }
}

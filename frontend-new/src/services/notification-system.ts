/**
 * Notification System
 * Toast notifications, in-app notifications, and push notifications
 */

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface ToastOptions {
  duration?: number;
  position?: NotificationPosition;
  action?: {
    label: string;
    onClick: () => void;
  };
}

type NotificationListener = (notification: Notification) => void;

export class NotificationSystem {
  private notifications: Notification[] = [];
  private listeners: Set<NotificationListener> = new Set();
  private maxNotifications: number = 50;

  constructor() {
    // Load persisted notifications
    this.loadNotifications();
    
    // Request permission for browser notifications
    this.requestPermission();
  }

  private async requestPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }

  private loadNotifications() {
    try {
      const stored = localStorage.getItem('terraforge-notifications');
      if (stored) {
        this.notifications = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load notifications:', e);
    }
  }

  private saveNotifications() {
    try {
      // Keep only last N notifications
      const toSave = this.notifications.slice(-this.maxNotifications);
      localStorage.setItem('terraforge-notifications', JSON.stringify(toSave));
    } catch (e) {
      console.error('Failed to save notifications:', e);
    }
  }

  private notify(notification: Notification) {
    this.notifications.push(notification);
    this.saveNotifications();
    
    // Notify all listeners
    this.listeners.forEach((listener) => listener(notification));
  }

  subscribe(listener: NotificationListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  toast(
    type: NotificationType,
    title: string,
    message: string,
    options: ToastOptions = {}
  ): string {
    const notification: Notification = {
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      title,
      message,
      duration: options.duration ?? (type === 'error' ? 10000 : 5000),
      timestamp: Date.now(),
      read: false,
      action: options.action,
    };

    this.notify(notification);
    
    // Show browser notification if permitted
    if (type === 'error' || type === 'warning') {
      this.showBrowserNotification(notification);
    }

    return notification.id;
  }

  success(title: string, message: string, options?: ToastOptions): string {
    return this.toast('success', title, message, options);
  }

  error(title: string, message: string, options?: ToastOptions): string {
    return this.toast('error', title, message, options);
  }

  warning(title: string, message: string, options?: ToastOptions): string {
    return this.toast('warning', title, message, options);
  }

  info(title: string, message: string, options?: ToastOptions): string {
    return this.toast('info', title, message, options);
  }

  private showBrowserNotification(notification: Notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      const browserNotif = new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.svg',
        badge: '/favicon.svg',
        tag: notification.id,
      });

      browserNotif.onclick = () => {
        window.focus();
        notification.action?.onClick();
        browserNotif.close();
      };
    }
  }

  getAll(): Notification[] {
    return [...this.notifications];
  }

  getUnread(): Notification[] {
    return this.notifications.filter((n) => !n.read);
  }

  markAsRead(id: string) {
    const notification = this.notifications.find((n) => n.id === id);
    if (notification) {
      notification.read = true;
      this.saveNotifications();
    }
  }

  markAllAsRead() {
    this.notifications.forEach((n) => (n.read = true));
    this.saveNotifications();
  }

  delete(id: string) {
    this.notifications = this.notifications.filter((n) => n.id !== id);
    this.saveNotifications();
  }

  clear() {
    this.notifications = [];
    this.saveNotifications();
  }

  getUnreadCount(): number {
    return this.notifications.filter((n) => !n.read).length;
  }
}

export const notificationSystem = new NotificationSystem();

// Helper functions for easy import
export const showNotification = (
  type: NotificationType,
  title: string,
  message: string,
  options?: ToastOptions
) => notificationSystem.toast(type, title, message, options);

export const showSuccess = (title: string, message: string, options?: ToastOptions) =>
  notificationSystem.success(title, message, options);

export const showError = (title: string, message: string, options?: ToastOptions) =>
  notificationSystem.error(title, message, options);

export const showWarning = (title: string, message: string, options?: ToastOptions) =>
  notificationSystem.warning(title, message, options);

export const showInfo = (title: string, message: string, options?: ToastOptions) =>
  notificationSystem.info(title, message, options);

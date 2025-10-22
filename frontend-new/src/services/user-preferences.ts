/**
 * User Preferences System
 * Manages user settings, preferences, and customization
 */

export interface UserPreferences {
  // Appearance
  theme: 'light' | 'dark' | 'system';
  colorScheme: string;
  fontSize: 'small' | 'medium' | 'large';
  compactMode: boolean;
  
  // Behavior
  autoSave: boolean;
  autoSaveInterval: number; // seconds
  confirmBeforeDelete: boolean;
  showTutorials: boolean;
  
  // Notifications
  enableNotifications: boolean;
  enableSounds: boolean;
  notificationPosition: 'top-right' | 'bottom-right' | 'top-left' | 'bottom-left';
  
  // Generation
  defaultResolution: number;
  defaultQuality: 'low' | 'medium' | 'high' | 'ultra';
  defaultExportFormat: string;
  rememberLastSettings: boolean;
  
  // Collaboration
  showLiveCursors: boolean;
  enableRealTimeSync: boolean;
  showUserPresence: boolean;
  
  // Privacy
  analyticsEnabled: boolean;
  crashReportsEnabled: boolean;
  shareUsageData: boolean;
  
  // Advanced
  developerMode: boolean;
  experimentalFeatures: boolean;
  cacheSize: number; // MB
}

const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'system',
  colorScheme: 'blue',
  fontSize: 'medium',
  compactMode: false,
  autoSave: true,
  autoSaveInterval: 30,
  confirmBeforeDelete: true,
  showTutorials: true,
  enableNotifications: true,
  enableSounds: true,
  notificationPosition: 'top-right',
  defaultResolution: 1024,
  defaultQuality: 'high',
  defaultExportFormat: 'godot',
  rememberLastSettings: true,
  showLiveCursors: true,
  enableRealTimeSync: true,
  showUserPresence: true,
  analyticsEnabled: true,
  crashReportsEnabled: true,
  shareUsageData: true,
  developerMode: false,
  experimentalFeatures: false,
  cacheSize: 100,
};

type PreferenceListener = (preferences: UserPreferences) => void;

export class UserPreferencesManager {
  private preferences: UserPreferences;
  private listeners: Set<PreferenceListener> = new Set();
  private storageKey = 'terraforge-preferences';

  constructor() {
    this.preferences = this.loadPreferences();
  }

  private loadPreferences(): UserPreferences {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_PREFERENCES, ...parsed };
      }
    } catch (e) {
      console.error('Failed to load preferences:', e);
    }
    return { ...DEFAULT_PREFERENCES };
  }

  private savePreferences() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.preferences));
      this.notifyListeners();
    } catch (e) {
      console.error('Failed to save preferences:', e);
    }
  }

  private notifyListeners() {
    this.listeners.forEach((listener) => listener(this.preferences));
  }

  subscribe(listener: PreferenceListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  get(): UserPreferences {
    return { ...this.preferences };
  }

  set(preferences: Partial<UserPreferences>) {
    this.preferences = { ...this.preferences, ...preferences };
    this.savePreferences();
  }

  reset() {
    this.preferences = { ...DEFAULT_PREFERENCES };
    this.savePreferences();
  }

  // Convenience getters
  getTheme(): string {
    return this.preferences.theme;
  }

  getAutoSaveInterval(): number {
    return this.preferences.autoSaveInterval * 1000; // Convert to ms
  }

  isFeatureEnabled(feature: keyof UserPreferences): boolean {
    return Boolean(this.preferences[feature]);
  }

  // Export/Import preferences
  export(): string {
    return JSON.stringify(this.preferences, null, 2);
  }

  import(json: string): boolean {
    try {
      const imported = JSON.parse(json);
      this.set(imported);
      return true;
    } catch (e) {
      console.error('Failed to import preferences:', e);
      return false;
    }
  }
}

export const userPreferences = new UserPreferencesManager();

// Helper hooks for React
export const usePreference = <K extends keyof UserPreferences>(
  key: K
): [UserPreferences[K], (value: UserPreferences[K]) => void] => {
  const value = userPreferences.get()[key];
  
  const setValue = (newValue: UserPreferences[K]) => {
    userPreferences.set({ [key]: newValue } as Partial<UserPreferences>);
  };
  
  return [value, setValue];
};

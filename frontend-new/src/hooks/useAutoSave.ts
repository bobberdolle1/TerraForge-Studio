import { useEffect, useRef } from 'react';
import { notify } from '../utils/toast';

interface UseAutoSaveOptions<T> {
  data: T;
  onSave: (data: T) => void | Promise<void>;
  interval?: number; // milliseconds
  enabled?: boolean;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Auto-save Hook
 * Automatically saves data at regular intervals
 * 
 * @example
 * useAutoSave({
 *   data: formData,
 *   onSave: async (data) => await api.save(data),
 *   interval: 30000, // 30 seconds
 * });
 */
export function useAutoSave<T>({
  data,
  onSave,
  interval = 30000,
  enabled = true,
  onSuccess,
  onError,
}: UseAutoSaveOptions<T>) {
  const savedDataRef = useRef<T>(data);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isSavingRef = useRef(false);

  useEffect(() => {
    if (!enabled) return;

    const save = async () => {
      // Check if data has changed
      if (JSON.stringify(data) === JSON.stringify(savedDataRef.current)) {
        return;
      }

      // Skip if already saving
      if (isSavingRef.current) return;

      isSavingRef.current = true;

      try {
        await onSave(data);
        savedDataRef.current = data;
        
        if (onSuccess) {
          onSuccess();
        } else {
          notify.success('Auto-saved', { duration: 2000 });
        }
      } catch (error) {
        console.error('Auto-save failed:', error);
        
        if (onError) {
          onError(error as Error);
        } else {
          notify.error('Auto-save failed');
        }
      } finally {
        isSavingRef.current = false;
      }
    };

    // Set up auto-save interval
    timeoutRef.current = setInterval(save, interval);

    return () => {
      if (timeoutRef.current) {
        clearInterval(timeoutRef.current);
      }
    };
  }, [data, onSave, interval, enabled, onSuccess, onError]);

  // Manual save function
  const saveNow = async () => {
    if (isSavingRef.current) return;

    isSavingRef.current = true;

    try {
      await onSave(data);
      savedDataRef.current = data;
      notify.success('Saved successfully');
    } catch (error) {
      console.error('Save failed:', error);
      notify.error('Save failed');
      throw error;
    } finally {
      isSavingRef.current = false;
    }
  };

  return { saveNow, isSaving: isSavingRef.current };
}

export default useAutoSave;

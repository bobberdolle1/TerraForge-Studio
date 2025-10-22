import { useState, useCallback, useRef } from 'react';

export interface Command<T = any> {
  execute: () => void;
  undo: () => void;
  data?: T;
  description?: string;
}

interface UseUndoRedoOptions {
  maxHistorySize?: number;
}

/**
 * Undo/Redo Hook
 * Implements Command Pattern for state management
 * 
 * @example
 * const { execute, undo, redo, canUndo, canRedo, history } = useUndoRedo();
 * 
 * execute({
 *   execute: () => setState(newValue),
 *   undo: () => setState(oldValue),
 *   description: 'Update value'
 * });
 */
export function useUndoRedo<T = any>(options: UseUndoRedoOptions = {}) {
  const { maxHistorySize = 50 } = options;

  const [history, setHistory] = useState<Command<T>[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const isExecuting = useRef(false);

  const execute = useCallback((command: Command<T>) => {
    if (isExecuting.current) return;

    isExecuting.current = true;
    
    try {
      command.execute();

      setHistory((prev) => {
        // Remove any commands after current index
        const newHistory = prev.slice(0, currentIndex + 1);
        
        // Add new command
        newHistory.push(command);

        // Limit history size
        if (newHistory.length > maxHistorySize) {
          newHistory.shift();
          setCurrentIndex((idx) => Math.max(0, idx));
        } else {
          setCurrentIndex((idx) => idx + 1);
        }

        return newHistory;
      });
    } finally {
      isExecuting.current = false;
    }
  }, [currentIndex, maxHistorySize]);

  const undo = useCallback(() => {
    if (currentIndex < 0 || isExecuting.current) return;

    isExecuting.current = true;

    try {
      const command = history[currentIndex];
      command.undo();
      setCurrentIndex((idx) => idx - 1);
    } finally {
      isExecuting.current = false;
    }
  }, [currentIndex, history]);

  const redo = useCallback(() => {
    if (currentIndex >= history.length - 1 || isExecuting.current) return;

    isExecuting.current = true;

    try {
      const command = history[currentIndex + 1];
      command.execute();
      setCurrentIndex((idx) => idx + 1);
    } finally {
      isExecuting.current = false;
    }
  }, [currentIndex, history]);

  const clear = useCallback(() => {
    setHistory([]);
    setCurrentIndex(-1);
  }, []);

  const canUndo = currentIndex >= 0;
  const canRedo = currentIndex < history.length - 1;

  return {
    execute,
    undo,
    redo,
    clear,
    canUndo,
    canRedo,
    history,
    currentIndex,
  };
}

export default useUndoRedo;

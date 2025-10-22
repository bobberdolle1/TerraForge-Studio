/**
 * Draggable Hook
 * Makes elements draggable with custom data
 */

import { useRef, useEffect } from 'react';

interface DraggableOptions {
  data: any;
  onDragStart?: () => void;
  onDragEnd?: () => void;
  enabled?: boolean;
}

export function useDraggable<T extends HTMLElement = HTMLElement>({
  data,
  onDragStart,
  onDragEnd,
  enabled = true,
}: DraggableOptions) {
  const elementRef = useRef<T>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element || !enabled) return;

    const handleDragStart = (e: DragEvent) => {
      if (!e.dataTransfer) return;

      // Set drag data
      e.dataTransfer.effectAllowed = 'copy';
      e.dataTransfer.setData('application/json', JSON.stringify(data));

      // Set drag image (optional)
      if (element) {
        const rect = element.getBoundingClientRect();
        e.dataTransfer.setDragImage(element, rect.width / 2, rect.height / 2);
      }

      // Add dragging class
      element.classList.add('dragging');

      onDragStart?.();
    };

    const handleDragEnd = (_e: DragEvent) => {
      element.classList.remove('dragging');
      onDragEnd?.();
    };

    element.setAttribute('draggable', 'true');
    element.addEventListener('dragstart', handleDragStart);
    element.addEventListener('dragend', handleDragEnd);

    return () => {
      element.removeEventListener('dragstart', handleDragStart);
      element.removeEventListener('dragend', handleDragEnd);
      element.removeAttribute('draggable');
    };
  }, [data, onDragStart, onDragEnd, enabled]);

  return elementRef;
}


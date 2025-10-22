import React from 'react';
import { Undo, Redo } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';
import { Tooltip } from './Tooltip';

interface UndoRedoControlsProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  className?: string;
}

/**
 * Undo/Redo Controls Component
 * Provides UI for undo/redo functionality
 */
export const UndoRedoControls: React.FC<UndoRedoControlsProps> = ({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  className = '',
}) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Tooltip content="Undo (Ctrl+Z)" position="bottom">
        <AccessibleButton
          variant="ghost"
          size="sm"
          onClick={onUndo}
          disabled={!canUndo}
          aria-label="Undo"
        >
          <Undo className="w-4 h-4" />
        </AccessibleButton>
      </Tooltip>

      <Tooltip content="Redo (Ctrl+Shift+Z)" position="bottom">
        <AccessibleButton
          variant="ghost"
          size="sm"
          onClick={onRedo}
          disabled={!canRedo}
          aria-label="Redo"
        >
          <Redo className="w-4 h-4" />
        </AccessibleButton>
      </Tooltip>
    </div>
  );
};

export default UndoRedoControls;

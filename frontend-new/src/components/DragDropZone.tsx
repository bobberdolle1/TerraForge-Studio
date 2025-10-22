/**
 * Drag & Drop Zone Component
 * Visual drop zone for terrain generation batch queue
 */

import { useState } from 'react';
import { Upload, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { BoundingBox } from '../types';

interface DragDropZoneProps {
  onDrop: (bbox: BoundingBox, name?: string) => void;
  isVisible: boolean;
  className?: string;
}

export default function DragDropZone({ onDrop, isVisible, className = '' }: DragDropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    try {
      const data = e.dataTransfer.getData('application/json');
      if (!data) return;

      const { bbox, name } = JSON.parse(data);
      if (bbox && bbox.north && bbox.south && bbox.east && bbox.west) {
        onDrop(bbox, name || `Area ${new Date().toLocaleTimeString()}`);
      }
    } catch (error) {
      console.error('Failed to parse drop data:', error);
    }
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className={`${className} ${
          isDragOver
            ? 'bg-blue-50 dark:bg-blue-900 dark:bg-opacity-30 border-blue-500 border-dashed'
            : 'bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-600 border-dashed'
        } border-2 rounded-lg p-8 transition-all duration-200`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center text-center">
          <motion.div
            animate={{
              scale: isDragOver ? 1.1 : 1,
              rotate: isDragOver ? 5 : 0,
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            {isDragOver ? (
              <Plus className="w-16 h-16 text-blue-500 mb-4" />
            ) : (
              <Upload className="w-16 h-16 text-gray-400 mb-4" />
            )}
          </motion.div>

          <h3 className={`text-lg font-semibold mb-2 ${
            isDragOver ? 'text-blue-600 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'
          }`}>
            {isDragOver ? 'Drop to Add to Batch' : 'Drag Area Here'}
          </h3>

          <p className="text-sm text-gray-500 dark:text-gray-400">
            {isDragOver
              ? 'Release to add this area to the batch queue'
              : 'Select an area on the map and drag it here to add to batch processing'}
          </p>

          {isDragOver && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center space-x-2 text-xs text-blue-600 dark:text-blue-400"
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span>Ready to drop</span>
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}


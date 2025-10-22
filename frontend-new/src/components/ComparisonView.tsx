/**
 * Comparison View Component
 * Split-view for comparing two terrain generations side by side
 */

import { useState, useRef, useEffect } from 'react';
import { X, RotateCcw, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface ComparisonItem {
  id: string;
  name: string;
  imageUrl?: string;
  timestamp: number;
}

interface ComparisonViewProps {
  leftItem: ComparisonItem;
  rightItem: ComparisonItem;
  onClose: () => void;
  onSwap?: () => void;
}

export default function ComparisonView({ leftItem, rightItem, onClose, onSwap }: ComparisonViewProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging || !containerRef.current) return;

    const touch = e.touches[0];
    const rect = containerRef.current.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  useEffect(() => {
    const handleGlobalMouseUp = () => setIsDragging(false);
    
    if (isDragging) {
      window.addEventListener('mouseup', handleGlobalMouseUp);
      window.addEventListener('touchend', handleGlobalMouseUp);
    }

    return () => {
      window.removeEventListener('mouseup', handleGlobalMouseUp);
      window.removeEventListener('touchend', handleGlobalMouseUp);
    };
  }, [isDragging]);

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-bold">Terrain Comparison</h2>
              <div className="text-sm opacity-90">
                Drag the slider to compare
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {onSwap && (
                <button
                  onClick={onSwap}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition"
                  title="Swap sides"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Comparison Container */}
        <div
          ref={containerRef}
          className="relative bg-gray-100 dark:bg-gray-900 overflow-hidden"
          style={{ height: 'calc(90vh - 140px)' }}
          onMouseMove={handleMouseMove}
          onTouchMove={handleTouchMove}
          onMouseUp={handleMouseUp}
          onTouchEnd={handleMouseUp}
        >
          {/* Left Side (Before) */}
          <div className="absolute inset-0">
            {leftItem.imageUrl ? (
              <img
                src={leftItem.imageUrl}
                alt={leftItem.name}
                className="w-full h-full object-cover"
                draggable={false}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-200 dark:bg-gray-800">
                <div className="text-center">
                  <p className="text-gray-500 dark:text-gray-400">No preview available</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">{leftItem.name}</p>
                </div>
              </div>
            )}
            <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-4 py-2 rounded-lg">
              <div className="font-semibold">{leftItem.name}</div>
              <div className="text-xs opacity-75">{formatDate(leftItem.timestamp)}</div>
            </div>
          </div>

          {/* Right Side (After) */}
          <div
            className="absolute inset-0 overflow-hidden"
            style={{ clipPath: `inset(0 0 0 ${sliderPosition}%)` }}
          >
            {rightItem.imageUrl ? (
              <img
                src={rightItem.imageUrl}
                alt={rightItem.name}
                className="w-full h-full object-cover"
                draggable={false}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-300 dark:bg-gray-700">
                <div className="text-center">
                  <p className="text-gray-500 dark:text-gray-400">No preview available</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">{rightItem.name}</p>
                </div>
              </div>
            )}
            <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white px-4 py-2 rounded-lg">
              <div className="font-semibold">{rightItem.name}</div>
              <div className="text-xs opacity-75">{formatDate(rightItem.timestamp)}</div>
            </div>
          </div>

          {/* Slider */}
          <div
            className="absolute top-0 bottom-0 w-1 bg-white shadow-lg cursor-ew-resize z-10"
            style={{ left: `${sliderPosition}%` }}
            onMouseDown={handleMouseDown}
            onTouchStart={handleMouseDown}
          >
            {/* Slider Handle */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-xl">
              <div className="flex items-center space-x-1">
                <ChevronLeft className="w-4 h-4 text-gray-700" />
                <ChevronRight className="w-4 h-4 text-gray-700" />
              </div>
            </div>
          </div>

          {/* Instructions */}
          {!isDragging && (
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-75 text-white px-6 py-3 rounded-lg pointer-events-none">
              <p className="text-sm">Drag the slider to compare • Press ESC to close</p>
            </div>
          )}
        </div>

        {/* Footer with Stats */}
        <div className="bg-gray-50 dark:bg-gray-750 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500 dark:text-gray-400 mb-1">Before</div>
              <div className="font-medium text-gray-900 dark:text-white">{leftItem.name}</div>
            </div>
            <div className="text-right">
              <div className="text-gray-500 dark:text-gray-400 mb-1">After</div>
              <div className="font-medium text-gray-900 dark:text-white">{rightItem.name}</div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}


import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CursorPosition {
  userId: string;
  username: string;
  color: string;
  x: number;
  y: number;
  lastUpdate: number;
}

interface LiveCursorsProps {
  realtimeService?: any;
}

export const LiveCursors: React.FC<LiveCursorsProps> = ({ realtimeService }) => {
  const [cursors, setCursors] = useState<Map<string, CursorPosition>>(new Map());
  const [ownUserId] = useState(() => `user_${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    if (!realtimeService) return;

    // Listen for cursor updates from other users
    const handleCursorUpdate = (data: CursorPosition) => {
      if (data.userId === ownUserId) return;

      setCursors((prev) => {
        const newCursors = new Map(prev);
        newCursors.set(data.userId, {
          ...data,
          lastUpdate: Date.now(),
        });
        return newCursors;
      });
    };

    // Listen for user disconnect
    const handleUserLeft = (userId: string) => {
      setCursors((prev) => {
        const newCursors = new Map(prev);
        newCursors.delete(userId);
        return newCursors;
      });
    };

    realtimeService.on('cursor.moved', handleCursorUpdate);
    realtimeService.on('user.left', (data: any) => handleUserLeft(data.userId));

    // Send own cursor position
    const handleMouseMove = (e: MouseEvent) => {
      realtimeService.updateCursor(e.clientX, e.clientY);
    };

    document.addEventListener('mousemove', handleMouseMove);

    // Clean up stale cursors
    const cleanupInterval = setInterval(() => {
      const now = Date.now();
      setCursors((prev) => {
        const newCursors = new Map(prev);
        for (const [userId, cursor] of newCursors.entries()) {
          if (now - cursor.lastUpdate > 5000) {
            newCursors.delete(userId);
          }
        }
        return newCursors;
      });
    }, 1000);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      clearInterval(cleanupInterval);
    };
  }, [realtimeService, ownUserId]);

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      <AnimatePresence>
        {Array.from(cursors.values()).map((cursor) => (
          <motion.div
            key={cursor.userId}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{
              opacity: 1,
              scale: 1,
              x: cursor.x,
              y: cursor.y,
            }}
            exit={{ opacity: 0, scale: 0.5 }}
            transition={{
              type: 'spring',
              stiffness: 500,
              damping: 30,
            }}
            className="absolute"
            style={{ left: -12, top: -12 }}
          >
            {/* Cursor SVG */}
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
            >
              <path
                d="M5.65376 12.3673L11.6768 5.76768L11.1939 17.3377L8.04914 12.3673H5.65376Z"
                fill={cursor.color}
                stroke="white"
                strokeWidth="1.5"
              />
            </svg>

            {/* Username Label */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute left-6 top-0 px-2 py-1 rounded text-xs font-medium text-white whitespace-nowrap"
              style={{
                backgroundColor: cursor.color,
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
              }}
            >
              {cursor.username}
            </motion.div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default LiveCursors;

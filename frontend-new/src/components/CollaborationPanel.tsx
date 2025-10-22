import React, { useState, useEffect } from 'react';
import { Users, Circle, MessageSquare, AtSign } from 'lucide-react';

interface User {
  id: string;
  name: string;
  avatar: string;
  color: string;
  status: 'online' | 'away' | 'offline';
  cursor?: { x: number; y: number };
}

interface Comment {
  id: string;
  userId: string;
  userName: string;
  text: string;
  position: { x: number; y: number };
  timestamp: number;
  replies: Comment[];
}

export const CollaborationPanel: React.FC = () => {
  const [users, setUsers] = useState<User[]>([
    {
      id: '1',
      name: 'Current User',
      avatar: 'CU',
      color: '#3b82f6',
      status: 'online',
    },
  ]);

  const [comments, setComments] = useState<Comment[]>([]);
  const [showComments, setShowComments] = useState(false);

  const getStatusColor = (status: User['status']) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'away': return 'bg-yellow-500';
      case 'offline': return 'bg-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Active Users */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Users className="w-5 h-5" />
            Active Users ({users.length})
          </h3>
        </div>
        
        <div className="space-y-2">
          {users.map((user) => (
            <div
              key={user.id}
              className="flex items-center gap-3 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <div className="relative">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                  style={{ backgroundColor: user.color }}
                >
                  {user.avatar}
                </div>
                <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(user.status)}`} />
              </div>
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {user.name}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Comments */}
      <div className="p-4">
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
        >
          <MessageSquare className="w-5 h-5" />
          Comments ({comments.length})
        </button>

        {showComments && (
          <div className="mt-4 space-y-3">
            {comments.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No comments yet
              </p>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-medium text-sm text-gray-900 dark:text-white">
                      {comment.userName}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(comment.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {comment.text}
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CollaborationPanel;

import React, { useState } from 'react';
import { Trophy, Medal, Award, TrendingUp } from 'lucide-react';

interface LeaderboardEntry {
  rank: number;
  userId: string;
  username: string;
  score: number;
  terrainsGenerated: number;
  avatar: string;
  trend: 'up' | 'down' | 'same';
}

export const LeaderboardPanel: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly' | 'alltime'>('weekly');
  
  const leaderboard: LeaderboardEntry[] = [
    {
      rank: 1,
      userId: '1',
      username: 'TerrainMaster',
      score: 15420,
      terrainsGenerated: 342,
      avatar: '🏔️',
      trend: 'up',
    },
    {
      rank: 2,
      userId: '2',
      username: 'MapCreator',
      score: 12850,
      terrainsGenerated: 287,
      avatar: '🗺️',
      trend: 'same',
    },
    {
      rank: 3,
      userId: '3',
      username: 'GeoWizard',
      score: 11230,
      terrainsGenerated: 251,
      avatar: '🧙',
      trend: 'down',
    },
  ];

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Trophy className="w-6 h-6 text-yellow-500" />;
      case 2: return <Medal className="w-6 h-6 text-gray-400" />;
      case 3: return <Award className="w-6 h-6 text-amber-600" />;
      default: return <span className="text-lg font-bold text-gray-500">#{rank}</span>;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Leaderboard
      </h2>

      {/* Timeframe Selector */}
      <div className="flex gap-2 mb-6">
        {(['daily', 'weekly', 'monthly', 'alltime'] as const).map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`px-4 py-2 rounded-lg capitalize transition-colors ${
              timeframe === tf
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {tf === 'alltime' ? 'All Time' : tf}
          </button>
        ))}
      </div>

      {/* Leaderboard List */}
      <div className="space-y-3">
        {leaderboard.map((entry) => (
          <div
            key={entry.userId}
            className={`flex items-center gap-4 p-4 rounded-lg transition-all ${
              entry.rank <= 3
                ? 'bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800'
                : 'bg-gray-50 dark:bg-gray-700'
            }`}
          >
            {/* Rank */}
            <div className="flex items-center justify-center w-12">
              {getRankIcon(entry.rank)}
            </div>

            {/* Avatar */}
            <div className="text-3xl">{entry.avatar}</div>

            {/* User Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900 dark:text-white">
                  {entry.username}
                </span>
                {entry.trend === 'up' && (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                )}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {entry.terrainsGenerated} terrains generated
              </div>
            </div>

            {/* Score */}
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {entry.score.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">points</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LeaderboardPanel;

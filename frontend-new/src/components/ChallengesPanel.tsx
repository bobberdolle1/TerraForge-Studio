import React, { useState } from 'react';
import { Target, Clock, Award, Zap, Users } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';
import useLocalStorage from '../hooks/useLocalStorage';

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'time' | 'creative' | 'technical';
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  timeLimit?: number; // seconds
  reward: {
    xp: number;
    badge?: string;
  };
  requirements: string[];
  progress: number;
  maxProgress: number;
  expiresAt?: number;
  participants?: number;
}

export const ChallengesPanel: React.FC = () => {
  const [activeChallenges, setActiveChallenges] = useLocalStorage<Challenge[]>(
    'terraforge-challenges',
    [
      {
        id: 'weekly_speedrun',
        title: 'Speed Terrain',
        description: 'Generate a 10km² terrain in under 60 seconds',
        type: 'time',
        difficulty: 'medium',
        timeLimit: 60,
        reward: { xp: 500, badge: '⚡' },
        requirements: ['Area: 10km²', 'Quality: High', 'Time: <60s'],
        progress: 0,
        maxProgress: 1,
        expiresAt: Date.now() + 604800000, // 7 days
        participants: 234,
      },
      {
        id: 'creative_island',
        title: 'Perfect Island',
        description: 'Create a realistic island with mountains and beaches',
        type: 'creative',
        difficulty: 'hard',
        reward: { xp: 1000, badge: '🏝️' },
        requirements: ['Mountains', 'Beaches', 'Realistic erosion', 'Community vote >4.5'],
        progress: 3,
        maxProgress: 4,
        expiresAt: Date.now() + 604800000,
        participants: 156,
      },
      {
        id: 'tech_all_engines',
        title: 'Multi-Engine Export',
        description: 'Export the same terrain to all 4 game engines',
        type: 'technical',
        difficulty: 'easy',
        reward: { xp: 300 },
        requirements: ['Godot', 'Unity', 'Unreal', 'glTF'],
        progress: 2,
        maxProgress: 4,
        participants: 89,
      },
    ]
  );

  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  const difficultyColors = {
    easy: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    hard: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
    expert: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
  };

  const typeIcons = {
    time: <Zap className="w-5 h-5" />,
    creative: <Target className="w-5 h-5" />,
    technical: <Award className="w-5 h-5" />,
  };

  const filteredChallenges = activeChallenges.filter(
    (c) => selectedDifficulty === 'all' || c.difficulty === selectedDifficulty
  );

  const formatTimeRemaining = (expiresAt?: number) => {
    if (!expiresAt) return 'No limit';
    const remaining = expiresAt - Date.now();
    const days = Math.floor(remaining / 86400000);
    const hours = Math.floor((remaining % 86400000) / 3600000);
    return `${days}d ${hours}h`;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Weekly Challenges
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Complete challenges to earn XP and exclusive badges
        </p>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        {['all', 'easy', 'medium', 'hard', 'expert'].map((diff) => (
          <button
            key={diff}
            onClick={() => setSelectedDifficulty(diff)}
            className={`px-4 py-2 rounded-lg capitalize transition-colors ${
              selectedDifficulty === diff
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {diff}
          </button>
        ))}
      </div>

      {/* Challenges Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredChallenges.map((challenge) => (
          <div
            key={challenge.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border-2 border-transparent hover:border-blue-500 transition-all"
          >
            {/* Header */}
            <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-600 text-white rounded-lg">
                    {typeIcons[challenge.type]}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                      {challenge.title}
                    </h3>
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium capitalize ${
                        difficultyColors[challenge.difficulty]
                      }`}
                    >
                      {challenge.difficulty}
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                {challenge.description}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                {challenge.expiresAt && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatTimeRemaining(challenge.expiresAt)}
                  </span>
                )}
                {challenge.participants && (
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {challenge.participants} playing
                  </span>
                )}
              </div>
            </div>

            {/* Body */}
            <div className="p-6">
              {/* Requirements */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Requirements
                </h4>
                <ul className="space-y-1">
                  {challenge.requirements.map((req, i) => (
                    <li
                      key={i}
                      className={`text-sm flex items-center gap-2 ${
                        i < challenge.progress
                          ? 'text-green-600 dark:text-green-400 line-through'
                          : 'text-gray-600 dark:text-gray-400'
                      }`}
                    >
                      <span className="w-4 h-4 rounded-full border-2 flex items-center justify-center">
                        {i < challenge.progress && '✓'}
                      </span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Progress */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {challenge.progress}/{challenge.maxProgress}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${(challenge.progress / challenge.maxProgress) * 100}%`,
                    }}
                  />
                </div>
              </div>

              {/* Reward */}
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg mb-4">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Reward
                </span>
                <div className="flex items-center gap-2">
                  {challenge.reward.badge && (
                    <span className="text-2xl">{challenge.reward.badge}</span>
                  )}
                  <span className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                    {challenge.reward.xp} XP
                  </span>
                </div>
              </div>

              {/* Action */}
              <AccessibleButton
                variant={challenge.progress === challenge.maxProgress ? 'primary' : 'secondary'}
                className="w-full"
                disabled={challenge.progress === challenge.maxProgress}
              >
                {challenge.progress === challenge.maxProgress
                  ? 'Completed! 🎉'
                  : 'Start Challenge'}
              </AccessibleButton>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChallengesPanel;

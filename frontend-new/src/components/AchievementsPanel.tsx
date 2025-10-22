import React, { useState } from 'react';
import { Trophy, Star, Medal, Award, Lock, Check } from 'lucide-react';
import useLocalStorage from '../hooks/useLocalStorage';

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  unlocked: boolean;
  progress: number;
  maxProgress: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  reward?: string;
}

export const AchievementsPanel: React.FC = () => {
  const [achievements, setAchievements] = useLocalStorage<Achievement[]>('terraforge-achievements', [
    {
      id: 'first_terrain',
      name: 'First Steps',
      description: 'Generate your first terrain',
      icon: <Star className="w-6 h-6" />,
      unlocked: true,
      progress: 1,
      maxProgress: 1,
      rarity: 'common',
    },
    {
      id: 'terrain_master',
      name: 'Terrain Master',
      description: 'Generate 100 terrains',
      icon: <Trophy className="w-6 h-6" />,
      unlocked: false,
      progress: 45,
      maxProgress: 100,
      rarity: 'rare',
    },
    {
      id: 'exporter_pro',
      name: 'Export Professional',
      description: 'Export to all game engines',
      icon: <Medal className="w-6 h-6" />,
      unlocked: false,
      progress: 3,
      maxProgress: 4,
      rarity: 'epic',
    },
    {
      id: 'speed_demon',
      name: 'Speed Demon',
      description: 'Generate terrain in under 1 minute',
      icon: <Award className="w-6 h-6" />,
      unlocked: true,
      progress: 1,
      maxProgress: 1,
      rarity: 'legendary',
      reward: '100 XP',
    },
  ]);

  const [selectedCategory, setSelectedCategory] = useState<'all' | 'unlocked' | 'locked'>('all');

  const rarityColors = {
    common: 'from-gray-400 to-gray-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-orange-600',
  };

  const filteredAchievements = achievements.filter((a) => {
    if (selectedCategory === 'unlocked') return a.unlocked;
    if (selectedCategory === 'locked') return !a.unlocked;
    return true;
  });

  const totalUnlocked = achievements.filter((a) => a.unlocked).length;
  const totalXP = achievements.filter((a) => a.unlocked && a.reward).length * 100;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Achievements
        </h1>
        <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
          <span>{totalUnlocked} / {achievements.length} Unlocked</span>
          <span>{totalXP} Total XP</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Overall Progress
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round((totalUnlocked / achievements.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all"
            style={{ width: `${(totalUnlocked / achievements.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {(['all', 'unlocked', 'locked'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg transition-colors capitalize ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredAchievements.map((achievement) => (
          <div
            key={achievement.id}
            className={`relative p-6 rounded-lg border-2 transition-all ${
              achievement.unlocked
                ? 'bg-white dark:bg-gray-800 border-transparent shadow-lg'
                : 'bg-gray-50 dark:bg-gray-900 border-gray-300 dark:border-gray-700 opacity-75'
            }`}
          >
            {/* Rarity Gradient Border */}
            {achievement.unlocked && (
              <div className={`absolute inset-0 bg-gradient-to-r ${rarityColors[achievement.rarity]} opacity-20 rounded-lg`} />
            )}

            <div className="relative flex items-start gap-4">
              {/* Icon */}
              <div className={`p-3 rounded-lg ${
                achievement.unlocked
                  ? `bg-gradient-to-br ${rarityColors[achievement.rarity]} text-white`
                  : 'bg-gray-300 dark:bg-gray-700 text-gray-500'
              }`}>
                {achievement.unlocked ? achievement.icon : <Lock className="w-6 h-6" />}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                    {achievement.name}
                  </h3>
                  {achievement.unlocked && (
                    <Check className="w-5 h-5 text-green-500" />
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {achievement.description}
                </p>

                {/* Progress Bar */}
                {!achievement.unlocked && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Progress
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {achievement.progress} / {achievement.maxProgress}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{ width: `${(achievement.progress / achievement.maxProgress) * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Reward */}
                {achievement.reward && achievement.unlocked && (
                  <div className="mt-2 px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs rounded inline-block">
                    🎁 {achievement.reward}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AchievementsPanel;

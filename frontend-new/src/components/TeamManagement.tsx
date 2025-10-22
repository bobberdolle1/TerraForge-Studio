import React, { useState } from 'react';
import { Users, UserPlus, Crown, Shield } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  joinedAt: number;
}

export const TeamManagement: React.FC = () => {
  const [members] = useState<TeamMember[]>([
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'owner',
      joinedAt: Date.now(),
    },
  ]);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Team Management</h1>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Invite Member</h2>
        <div className="flex gap-4">
          <input
            type="email"
            placeholder="Email"
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <AccessibleButton variant="primary" leftIcon={<UserPlus className="w-4 h-4" />}>
            Invite
          </AccessibleButton>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        {members.map((member) => (
          <div key={member.id} className="p-4 border-b flex items-center justify-between">
            <div>
              <div className="font-semibold">{member.name}</div>
              <div className="text-sm text-gray-600">{member.email}</div>
            </div>
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm flex items-center gap-1">
              {member.role === 'owner' && <Crown className="w-4 h-4" />}
              {member.role}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TeamManagement;

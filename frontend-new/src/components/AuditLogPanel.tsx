import React, { useState } from 'react';
import { Shield, Clock, User, Activity, Filter } from 'lucide-react';

interface AuditLog {
  id: string;
  timestamp: number;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceId: string;
  ipAddress: string;
  userAgent: string;
  status: 'success' | 'failure' | 'warning';
  details?: any;
}

export const AuditLogPanel: React.FC = () => {
  const [logs] = useState<AuditLog[]>([
    {
      id: '1',
      timestamp: Date.now() - 300000,
      userId: 'user123',
      username: 'admin@terraforge.com',
      action: 'terrain.generate',
      resource: 'terrain',
      resourceId: 'trn_abc123',
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0',
      status: 'success',
    },
    {
      id: '2',
      timestamp: Date.now() - 600000,
      userId: 'user456',
      username: 'user@example.com',
      action: 'user.login',
      resource: 'auth',
      resourceId: 'session_xyz',
      ipAddress: '192.168.1.101',
      userAgent: 'Mozilla/5.0',
      status: 'success',
    },
    {
      id: '3',
      timestamp: Date.now() - 900000,
      userId: 'user789',
      username: 'test@example.com',
      action: 'project.delete',
      resource: 'project',
      resourceId: 'prj_def456',
      ipAddress: '192.168.1.102',
      userAgent: 'Mozilla/5.0',
      status: 'failure',
      details: { error: 'Insufficient permissions' },
    },
  ]);

  const [filter, setFilter] = useState<'all' | 'success' | 'failure'>('all');

  const statusColors = {
    success: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    failure: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  };

  const filteredLogs = logs.filter(
    (log) => filter === 'all' || log.status === filter
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
          <Shield className="w-8 h-8 text-blue-600" />
          Audit Logs
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Security and compliance audit trail
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          <Filter className="w-4 h-4" />
          All Events
        </button>
        <button
          onClick={() => setFilter('success')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'success'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Success
        </button>
        <button
          onClick={() => setFilter('failure')}
          className={`px-4 py-2 rounded-lg ${
            filter === 'failure'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Failures
        </button>
      </div>

      {/* Logs Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  IP Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="text-gray-900 dark:text-white font-medium">
                          {log.username}
                        </div>
                        <div className="text-gray-500 dark:text-gray-400 text-xs">
                          {log.userId}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-blue-500" />
                      <code className="text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        {log.action}
                      </code>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {log.resource}
                    <br />
                    <span className="text-xs text-gray-500">{log.resourceId}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {log.ipAddress}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        statusColors[log.status]
                      }`}
                    >
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {logs.length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Events</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {logs.filter((l) => l.status === 'success').length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Successful</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-red-600">
            {logs.filter((l) => l.status === 'failure').length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Failed</div>
        </div>
      </div>
    </div>
  );
};

export default AuditLogPanel;

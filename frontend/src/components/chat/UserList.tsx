/**
 * User list component showing online users.
 */

import React from 'react';
import { User } from '../../types';

interface UserListProps {
  users: User[];
}

export const UserList: React.FC<UserListProps> = ({ users }) => {
  const onlineUsers = users.filter(user => user.isOnline);

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">Online:</span>
      <div className="flex -space-x-2">
        {onlineUsers.slice(0, 5).map((user) => (
          <div
            key={user.id}
            className="w-6 h-6 bg-blue-500 rounded-full border-2 border-white flex items-center justify-center text-xs text-white font-medium"
            title={user.name}
          >
            {user.name.charAt(0).toUpperCase()}
          </div>
        ))}
        {onlineUsers.length > 5 && (
          <div
            className="w-6 h-6 bg-gray-400 rounded-full border-2 border-white flex items-center justify-center text-xs text-white font-medium"
            title={`+${onlineUsers.length - 5} more`}
          >
            +{onlineUsers.length - 5}
          </div>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export function UsersPage({ onOpenCreateUserModal }) {
  const { isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.getUsers({
        department: deptFilter || undefined,
      });
      setUsers(res);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [deptFilter]);

  const handleToggleStatus = async (user) => {
    if (!isAdmin) return;
    const action = user.is_active ? 'deactivate' : 'activate';
    if (!window.confirm(`Are you sure you want to ${action} ${user.name}?`)) return;

    try {
      await api.toggleUserStatus(user.id, !user.is_active);
      fetchUsers();
    } catch (err) {
      alert(err.message);
    }
  };

  const filteredUsers = users.filter((u) => {
    const term = search.toLowerCase();
    return (
      u.name.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term) ||
      u.employee_id.toLowerCase().includes(term) ||
      u.designation.toLowerCase().includes(term)
    );
  });

  return (
    <div className="page-wrapper">
      <div className="section-toolbar">
        <div>
          <h2 className="section-title">Employee Directory</h2>
          <p className="section-desc">Manage team hierarchy, active statuses, and departmental assignments</p>
        </div>

        {isAdmin && (
          <button className="primary-btn" onClick={onOpenCreateUserModal}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            <span>Add Team Member</span>
          </button>
        )}
      </div>

      <div className="filter-bar">
        <div className="search-input-wrapper">
          <svg className="search-icon" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search by name, email, employee code, or designation..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="content-card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Employee Code</th>
                <th>Full Name & Email</th>
                <th>Department</th>
                <th>Designation</th>
                <th>Role</th>
                <th>Reporting Manager</th>
                <th>Status</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin ? 8 : 7} className="empty-state">
                    No employee records found.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <code className="code-pill">{u.employee_id}</code>
                    </td>
                    <td>
                      <div className="user-cell">
                        <div className="avatar-sm">{u.name.charAt(0)}</div>
                        <div>
                          <strong>{u.name}</strong>
                          <span className="sub-code">{u.email}</span>
                        </div>
                      </div>
                    </td>
                    <td>{u.department}</td>
                    <td>{u.designation}</td>
                    <td>
                      <span className="role-tag">{u.roles.join(', ')}</span>
                    </td>
                    <td>{u.manager?.name || '—'}</td>
                    <td>
                      {u.is_active ? (
                        <span className="status-badge active">Active</span>
                      ) : (
                        <span className="status-badge inactive">Deactivated</span>
                      )}
                    </td>
                    {isAdmin && (
                      <td>
                        <button
                          className={`action-btn ${u.is_active ? 'danger' : 'success'}`}
                          onClick={() => handleToggleStatus(u)}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

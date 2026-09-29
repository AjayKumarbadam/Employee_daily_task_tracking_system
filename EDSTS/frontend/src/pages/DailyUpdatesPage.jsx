import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { StatusBadge } from '../components/Badges';

export function DailyUpdatesPage() {
  const { user, isAdmin, isManager } = useAuth();
  const [updates, setUpdates] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchUpdates = async () => {
    try {
      setLoading(true);
      const params = {};
      if (fromDate) params.from_date = fromDate;
      if (toDate) params.to_date = toDate;
      if (selectedUser) params.user_id = selectedUser;

      const res = await api.getDailyUpdates(params);
      setUpdates(res);

      if (isAdmin || isManager) {
        const uRes = await api.getUsers();
        setUsersList(uRes);
      }
    } catch (err) {
      console.error('Failed to load updates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpdates();
  }, [fromDate, toDate, selectedUser]);

  const filteredUpdates = updates.filter((u) => {
    const term = searchTerm.toLowerCase();
    return (
      (u.task_title && u.task_title.toLowerCase().includes(term)) ||
      (u.user_name && u.user_name.toLowerCase().includes(term)) ||
      (u.remarks && u.remarks.toLowerCase().includes(term))
    );
  });

  return (
    <div className="page-wrapper">
      <div className="section-toolbar">
        <div>
          <h2 className="section-title">Daily Progress Logs</h2>
          <p className="section-desc">Audit trail of daily task completions, blocker reports, and developer remarks</p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="search-input-wrapper">
          <svg className="search-icon" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search remarks, task names, or team members..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="select-filters">
          <div className="date-range-group">
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              title="From Date"
            />
            <span className="date-sep">to</span>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              title="To Date"
            />
          </div>

          {(isAdmin || isManager) && (
            <select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)}>
              <option value="">All Team Members</option>
              {usersList.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name} ({u.employee_id})
                </option>
              ))}
            </select>
          )}

          {(fromDate || toDate || selectedUser) && (
            <button
              className="text-btn"
              onClick={() => {
                setFromDate('');
                setToDate('');
                setSelectedUser('');
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* History Table */}
      <div className="content-card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Employee</th>
                <th>Task</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Daily Remarks & Deliverables</th>
              </tr>
            </thead>
            <tbody>
              {filteredUpdates.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-state">
                    No daily progress updates recorded for the selected period.
                  </td>
                </tr>
              ) : (
                filteredUpdates.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <span className="log-date">{item.update_date}</span>
                    </td>
                    <td>
                      <div className="user-cell">
                        <div className="avatar-xs">{item.user_name?.charAt(0) || 'U'}</div>
                        <div>
                          <strong>{item.user_name}</strong>
                          <span className="sub-code">{item.user_employee_id}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <strong>{item.task_title || 'Untitled Task'}</strong>
                    </td>
                    <td><StatusBadge status={item.status_name} /></td>
                    <td>
                      <span className="progress-badge">{item.progress_percentage}%</span>
                    </td>
                    <td className="remarks-cell">
                      <p className="remarks-quote">"{item.remarks}"</p>
                    </td>
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

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/Badges';

export function TasksPage({ onOpenSubmitModal, onOpenCreateTaskModal }) {
  const { user, isAdmin, isManager } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const res = await api.getTasks({
        priority: priorityFilter || undefined,
      });
      setTasks(res);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [priorityFilter]);

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.current_assignment?.assignee?.name &&
        t.current_assignment.assignee.name.toLowerCase().includes(searchQuery.toLowerCase()));

    const statusName = t.latest_update?.status_name || 'NOT_STARTED';
    const matchesStatus = statusFilter ? statusName === statusFilter : true;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="page-wrapper">
      <div className="section-toolbar">
        <div>
          <h2 className="section-title">Task Assignments</h2>
          <p className="section-desc">Manage deliverables, deadlines, and assigned contributors</p>
        </div>

        {(isAdmin || isManager) && (
          <button className="primary-btn" onClick={onOpenCreateTaskModal}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Create New Task</span>
          </button>
        )}
      </div>

      {/* Search & Filter Controls */}
      <div className="filter-bar">
        <div className="search-input-wrapper">
          <svg className="search-icon" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search by task title, description, or employee name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="select-filters">
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="NOT_STARTED">Not Started</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="BLOCKED">Blocked</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Task Table */}
      <div className="content-card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Task Title</th>
                <th>Assignee</th>
                <th>Priority</th>
                <th>Due Date</th>
                <th>Current Status</th>
                <th>Progress</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTasks.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-state">
                    No matching tasks found.
                  </td>
                </tr>
              ) : (
                filteredTasks.map((task) => {
                  const assignee = task.current_assignment?.assignee;
                  const statusName = task.latest_update?.status_name || 'NOT_STARTED';
                  const progress = task.latest_update?.progress_percentage || 0;
                  const canSubmit = task.current_assignment?.user_id === user.id || isAdmin;

                  return (
                    <tr key={task.id}>
                      <td>
                        <div className="task-title-cell">
                          <strong>{task.title}</strong>
                          {task.description && <span className="task-desc">{task.description}</span>}
                        </div>
                      </td>
                      <td>
                        {assignee ? (
                          <div className="assignee-cell">
                            <div className="avatar-xs">{assignee.name.charAt(0)}</div>
                            <span>{assignee.name}</span>
                          </div>
                        ) : (
                          <span className="unassigned-text">Unassigned</span>
                        )}
                      </td>
                      <td><PriorityBadge priority={task.priority} /></td>
                      <td>
                        <span className="due-date">
                          {task.due_date}
                          {task.is_overdue && <span className="overdue-tag">OVERDUE</span>}
                        </span>
                      </td>
                      <td><StatusBadge status={statusName} /></td>
                      <td style={{ width: '150px' }}>
                        <div className="progress-cell">
                          <div className="progress-label">{progress}%</div>
                          <div className="progress-track">
                            <div
                              className={`progress-bar ${progress === 100 ? 'done' : ''}`}
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        {canSubmit ? (
                          <button
                            className="action-btn secondary"
                            onClick={() => onOpenSubmitModal(task)}
                          >
                            Update Progress
                          </button>
                        ) : (
                          <span className="view-only-text">Assigned</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

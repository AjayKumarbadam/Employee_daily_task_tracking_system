import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/Badges';

export function DashboardPage({ onOpenSubmitModal, onOpenCreateTaskModal }) {
  const { user, isAdmin, isManager, isEmployee } = useAuth();
  const [data, setData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      if (isAdmin || isManager) {
        const res = await api.getManagerDashboard(selectedDate);
        setData(res);
      } else {
        const res = await api.getEmployeeDashboard(selectedDate);
        setData(res);
        const myTasks = await api.getTasks();
        setTasks(myTasks);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [selectedDate]);

  const summary = data?.summary || {};
  const employees = data?.employees || [];

  return (
    <div className="page-wrapper">
      {/* Top Filter Bar */}
      <div className="section-toolbar">
        <div>
          <h2 className="section-title">
            {isEmployee && !isManager && !isAdmin ? 'My Daily Overview' : 'Operational Summary'}
          </h2>
          <p className="section-desc">
            {isEmployee && !isManager && !isAdmin
              ? 'Track your daily deliverables, submit end-of-day progress, and flag blockers.'
              : 'Real-time daily task completion, status breakdown, and team tracking.'}
          </p>
        </div>

        <div className="toolbar-actions">
          <div className="date-input-group">
            <label htmlFor="dash-date">View Date:</label>
            <input
              id="dash-date"
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="date-picker-input"
            />
          </div>

          {(isAdmin || isManager) && (
            <button className="primary-btn" onClick={onOpenCreateTaskModal}>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>Assign New Task</span>
            </button>
          )}
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Total Active Tasks</span>
            <div className="metric-icon total">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" />
              </svg>
            </div>
          </div>
          <div className="metric-value">{summary.total_tasks || 0}</div>
          <div className="metric-subtext">Assigned in system</div>
        </div>

        <div className="metric-card success">
          <div className="metric-header">
            <span className="metric-title">Completed (100%)</span>
            <div className="metric-icon success">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <div className="metric-value">{summary.completed || 0}</div>
          <div className="metric-subtext">Finished deliverables</div>
        </div>

        <div className="metric-card info">
          <div className="metric-header">
            <span className="metric-title">In Progress</span>
            <div className="metric-icon info">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div className="metric-value">{summary.in_progress || 0}</div>
          <div className="metric-subtext">Currently active</div>
        </div>

        <div className="metric-card warning">
          <div className="metric-header">
            <span className="metric-title">Not Started</span>
            <div className="metric-icon warning">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="metric-value">{summary.not_started || 0}</div>
          <div className="metric-subtext">Queued for work</div>
        </div>

        <div className="metric-card danger">
          <div className="metric-header">
            <span className="metric-title">Blocked / Overdue</span>
            <div className="metric-icon danger">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          <div className="metric-value">{(summary.blocked || 0) + (summary.overdue || 0)}</div>
          <div className="metric-subtext">Needs attention</div>
        </div>
      </div>

      {/* Main Role-Specific Table Section */}
      {isAdmin || isManager ? (
        <div className="content-card">
          <div className="card-header">
            <div>
              <h3>Team Daily Submission Status</h3>
              <p>Overview of employees and whether they have submitted progress updates today</p>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Department</th>
                  <th>Total Tasks</th>
                  <th>Completed</th>
                  <th>In Progress</th>
                  <th>Blocked</th>
                  <th>Daily Log Status</th>
                </tr>
              </thead>
              <tbody>
                {employees.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty-state">No employee records found.</td>
                  </tr>
                ) : (
                  employees.map((emp) => (
                    <tr key={emp.user_id}>
                      <td>
                        <div className="user-cell">
                          <div className="avatar-sm">{emp.name.charAt(0)}</div>
                          <div>
                            <strong>{emp.name}</strong>
                            <span className="sub-code">{emp.employee_id}</span>
                          </div>
                        </div>
                      </td>
                      <td>{emp.department}</td>
                      <td><strong>{emp.total_assigned}</strong></td>
                      <td><span className="count-badge completed">{emp.completed}</span></td>
                      <td><span className="count-badge in-progress">{emp.in_progress}</span></td>
                      <td><span className="count-badge blocked">{emp.blocked}</span></td>
                      <td>
                        {emp.has_submitted_today ? (
                          <span className="status-indicator submitted">
                            <svg width="14" height="14" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            Submitted
                          </span>
                        ) : (
                          <span className="status-indicator pending">
                            <span className="pulse-dot" />
                            Pending Update
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="content-card">
          <div className="card-header">
            <div>
              <h3>My Assigned Tasks</h3>
              <p>Click "Submit Daily Status" to record today's progress percentage and remarks</p>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Task Title</th>
                  <th>Priority</th>
                  <th>Target Due Date</th>
                  <th>Current Status</th>
                  <th>Progress</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="empty-state">No tasks currently assigned to you.</td>
                  </tr>
                ) : (
                  tasks.map((task) => {
                    const latest = task.latest_update;
                    const statusName = latest?.status_name || 'NOT_STARTED';
                    const progress = latest?.progress_percentage || 0;
                    return (
                      <tr key={task.id}>
                        <td>
                          <div className="task-title-cell">
                            <strong>{task.title}</strong>
                            {task.description && <span className="task-desc">{task.description}</span>}
                          </div>
                        </td>
                        <td><PriorityBadge priority={task.priority} /></td>
                        <td>
                          <span className="due-date">
                            {task.due_date}
                            {task.is_overdue && <span className="overdue-tag">OVERDUE</span>}
                          </span>
                        </td>
                        <td><StatusBadge status={statusName} /></td>
                        <td style={{ width: '180px' }}>
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
                          <button
                            className="action-btn primary"
                            onClick={() => onOpenSubmitModal(task)}
                          >
                            Submit Daily Status
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

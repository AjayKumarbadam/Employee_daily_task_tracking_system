import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export function ReportsPage() {
  const { isAdmin, isManager } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReportData = async () => {
      try {
        setLoading(true);
        const [tList, uList] = await Promise.all([api.getTasks(), api.getUsers()]);
        setTasks(tList);
        setUsers(uList);
      } catch (err) {
        console.error('Failed to load report data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadReportData();
  }, []);

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.latest_update?.status_name === 'COMPLETED').length;
  const inProgressTasks = tasks.filter((t) => t.latest_update?.status_name === 'IN_PROGRESS').length;
  const blockedTasks = tasks.filter((t) => t.latest_update?.status_name === 'BLOCKED').length;
  const overdueTasks = tasks.filter((t) => t.is_overdue).length;

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Group by department
  const deptMap = {};
  users.forEach((u) => {
    if (!deptMap[u.department]) {
      deptMap[u.department] = { total: 0, completed: 0, in_progress: 0, blocked: 0 };
    }
  });

  tasks.forEach((t) => {
    const dept = t.current_assignment?.assignee?.department || 'Engineering';
    if (!deptMap[dept]) {
      deptMap[dept] = { total: 0, completed: 0, in_progress: 0, blocked: 0 };
    }
    deptMap[dept].total += 1;
    const st = t.latest_update?.status_name;
    if (st === 'COMPLETED') deptMap[dept].completed += 1;
    else if (st === 'IN_PROGRESS') deptMap[dept].in_progress += 1;
    else if (st === 'BLOCKED') deptMap[dept].blocked += 1;
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="page-wrapper">
      <div className="section-toolbar">
        <div>
          <h2 className="section-title">Organization Productivity Report</h2>
          <p className="section-desc">Performance summary, task distribution, and completion rates</p>
        </div>

        <button className="secondary-btn" onClick={handlePrint}>
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          <span>Print / Export PDF</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Overall Completion Rate</span>
          </div>
          <div className="metric-value" style={{ color: 'var(--primary)' }}>
            {completionRate}%
          </div>
          <div className="metric-subtext">{completedTasks} of {totalTasks} finished</div>
        </div>

        <div className="metric-card success">
          <div className="metric-header">
            <span className="metric-title">Resolved Deliverables</span>
          </div>
          <div className="metric-value">{completedTasks}</div>
          <div className="metric-subtext">Verified 100%</div>
        </div>

        <div className="metric-card info">
          <div className="metric-header">
            <span className="metric-title">Active Work Items</span>
          </div>
          <div className="metric-value">{inProgressTasks}</div>
          <div className="metric-subtext">Under active development</div>
        </div>

        <div className="metric-card danger">
          <div className="metric-header">
            <span className="metric-title">Overdue Deliverables</span>
          </div>
          <div className="metric-value">{overdueTasks}</div>
          <div className="metric-subtext">Past target due date</div>
        </div>
      </div>

      {/* Department Breakdown Table */}
      <div className="content-card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <div>
            <h3>Department Breakdown</h3>
            <p>Task status distribution aggregated by business unit</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Total Assigned</th>
                <th>Completed</th>
                <th>In Progress</th>
                <th>Blocked</th>
                <th>Completion Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(deptMap).map(([deptName, stats]) => {
                const rate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
                return (
                  <tr key={deptName}>
                    <td>
                      <strong>{deptName}</strong>
                    </td>
                    <td>{stats.total}</td>
                    <td><span className="count-badge completed">{stats.completed}</span></td>
                    <td><span className="count-badge in-progress">{stats.in_progress}</span></td>
                    <td><span className="count-badge blocked">{stats.blocked}</span></td>
                    <td>
                      <div className="progress-cell">
                        <div className="progress-label">{rate}%</div>
                        <div className="progress-track">
                          <div className="progress-bar done" style={{ width: `${rate}%` }} />
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

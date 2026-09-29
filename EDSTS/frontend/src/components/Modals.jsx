import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function SubmitDailyUpdateModal({ isOpen, onClose, task, onSuccess }) {
  if (!isOpen || !task) return null;

  const [statuses, setStatuses] = useState([]);
  const [statusId, setStatusId] = useState('');
  const [progress, setProgress] = useState(0);
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatuses = async () => {
      try {
        const res = await api.getTaskStatuses();
        setStatuses(res);
        const latest = task.latest_update;
        setStatusId(latest?.status_id || res[0]?.id || 1);
        setProgress(latest?.progress_percentage || 0);
        setRemarks(latest?.remarks || '');
      } catch (err) {
        console.error(err);
      }
    };
    fetchStatuses();
  }, [task]);

  const handleStatusChange = (newStatusId) => {
    setStatusId(newStatusId);
    const selected = statuses.find((s) => s.id === parseInt(newStatusId));
    if (selected?.name === 'COMPLETED') {
      setProgress(100);
    } else if (selected?.name === 'NOT_STARTED') {
      setProgress(0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (remarks.trim().length < 3) {
      setError('Please provide a meaningful remark of at least 3 characters.');
      return;
    }

    try {
      setLoading(true);
      await api.submitDailyUpdate({
        task_id: task.id,
        status_id: parseInt(statusId),
        progress_percentage: parseInt(progress),
        remarks: remarks.trim(),
      });
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit daily update.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <div className="modal-header">
          <div>
            <h3>Submit Daily Task Status</h3>
            <p className="modal-sub">Record today's work deliverables and progress</p>
          </div>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="modal-error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="task-preview-box">
              <span className="preview-label">Work Item</span>
              <h4>{task.title}</h4>
              {task.description && <p>{task.description}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="task-status-select">Current Status</label>
              <select
                id="task-status-select"
                className="custom-select"
                value={statusId}
                onChange={(e) => handleStatusChange(e.target.value)}
              >
                {statuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <div className="slider-header">
                <label htmlFor="progress-input">Progress Percentage</label>
                <span className="slider-value">{progress}%</span>
              </div>
              <input
                id="progress-input"
                type="range"
                min="0"
                max="100"
                value={progress}
                onChange={(e) => setProgress(e.target.value)}
                className="progress-slider"
              />
            </div>

            <div className="form-group">
              <label htmlFor="remarks-text">Daily Progress Remarks & Blockers</label>
              <textarea
                id="remarks-text"
                rows="3"
                placeholder="Detail what components you built or tested today, and mention any external roadblocks..."
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Submitting...' : 'Save & Submit Status'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function CreateTaskModal({ isOpen, onClose, onSuccess }) {
  if (!isOpen) return null;

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [dueDate, setDueDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [assigneeId, setAssigneeId] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const res = await api.getUsers({ is_active: true });
        setUsers(res);
      } catch (err) {
        console.error(err);
      }
    };
    loadUsers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      setLoading(true);
      await api.createTask({
        title,
        description,
        priority,
        due_date: dueDate,
        assigned_to_user_id: assigneeId || null,
      });
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create task.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <div className="modal-header">
          <div>
            <h3>Create & Assign Task</h3>
            <p className="modal-sub">Define deliverables and assign team ownership</p>
          </div>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="modal-error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Task Title</label>
              <input
                type="text"
                placeholder="e.g. Implement OAuth2 Refresh Token Rotation"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Description & Scope</label>
              <textarea
                rows="3"
                placeholder="Specify architectural criteria, acceptance goals, and dependencies..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Priority</label>
                <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>

              <div className="form-group">
                <label>Target Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Assignee</label>
              <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)}>
                <option value="">-- Select Team Member --</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} — {u.designation} ({u.department})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function CreateUserModal({ isOpen, onClose, onSuccess }) {
  if (!isOpen) return null;

  const [name, setName] = useState('');
  const [empId, setEmpId] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('Password@123');
  const [department, setDepartment] = useState('Engineering');
  const [designation, setDesignation] = useState('Software Engineer');
  const [role, setRole] = useState('EMPLOYEE');
  const [managerId, setManagerId] = useState('');
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchManagers = async () => {
      try {
        const res = await api.getUsers({ is_active: true });
        setManagers(res);
      } catch (err) {
        console.error(err);
      }
    };
    fetchManagers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      setLoading(true);
      await api.createUser({
        name,
        employee_id: empId,
        email,
        password,
        department,
        designation,
        roles: [role],
        manager_id: managerId || null,
      });
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create user account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <div className="modal-header">
          <div>
            <h3>Add Team Member</h3>
            <p className="modal-sub">Create a new organizational user account</p>
          </div>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="modal-error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-row">
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Ramesh Chandra"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Employee Code</label>
                <input
                  type="text"
                  placeholder="EMP204"
                  value={empId}
                  onChange={(e) => setEmpId(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Work Email</label>
                <input
                  type="email"
                  placeholder="ramesh@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Temporary Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Designation</label>
                <input
                  type="text"
                  value={designation}
                  onChange={(e) => setDesignation(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>System Role</label>
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="EMPLOYEE">Employee (Contributor)</option>
                  <option value="MANAGER">Manager (Team Lead)</option>
                  <option value="ADMIN">System Administrator</option>
                </select>
              </div>

              <div className="form-group">
                <label>Reporting Manager</label>
                <select value={managerId} onChange={(e) => setManagerId(e.target.value)}>
                  <option value="">-- None (Self) --</option>
                  {managers.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.department})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Adding...' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import React from 'react';

export function StatusBadge({ status }) {
  const normalized = (status || 'NOT_STARTED').toUpperCase();

  const styles = {
    COMPLETED: { bg: '#ECFDF5', text: '#065F46', border: '#A7F3D0', label: 'Completed' },
    IN_PROGRESS: { bg: '#EFF6FF', text: '#1E40AF', border: '#BFDBFE', label: 'In Progress' },
    NOT_STARTED: { bg: '#F8FAFC', text: '#475569', border: '#E2E8F0', label: 'Not Started' },
    BLOCKED: { bg: '#FEF2F2', text: '#991B1B', border: '#FECACA', label: 'Blocked' },
    CANCELLED: { bg: '#F1F5F9', text: '#64748B', border: '#CBD5E1', label: 'Cancelled' },
  };

  const current = styles[normalized] || styles.NOT_STARTED;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px 10px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: current.bg,
        color: current.text,
        border: `1px solid ${current.border}`,
        whiteSpace: 'nowrap',
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: current.text,
          marginRight: '6px',
        }}
      />
      {current.label}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  const normalized = (priority || 'MEDIUM').toUpperCase();

  const styles = {
    CRITICAL: { bg: '#FEF2F2', text: '#B91C1C', label: 'Critical' },
    HIGH: { bg: '#FFF7ED', text: '#C2410C', label: 'High' },
    MEDIUM: { bg: '#FEFCE8', text: '#854D0E', label: 'Medium' },
    LOW: { bg: '#F0FDF4', text: '#15803D', label: 'Low' },
  };

  const current = styles[normalized] || styles.MEDIUM;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: current.bg,
        color: current.text,
      }}
    >
      {current.label}
    </span>
  );
}

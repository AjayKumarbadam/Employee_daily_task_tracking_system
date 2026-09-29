import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { TasksPage } from './pages/TasksPage';
import { DailyUpdatesPage } from './pages/DailyUpdatesPage';
import { ReportsPage } from './pages/ReportsPage';
import { UsersPage } from './pages/UsersPage';
import { SubmitDailyUpdateModal, CreateTaskModal, CreateUserModal } from './components/Modals';

function MainApp() {
  const { user, loading, isAdmin, isManager, isEmployee } = useAuth();
  const [currentTab, setCurrentTab] = useState('dashboard');

  // Modals state
  const [selectedTask, setSelectedTask] = useState(null);
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
  const [isCreateTaskModalOpen, setIsCreateTaskModalOpen] = useState(false);
  const [isCreateUserModalOpen, setIsCreateUserModalOpen] = useState(false);

  // Key to trigger page reload
  const [refreshKey, setRefreshKey] = useState(0);

  if (loading) {
    return (
      <div className="fullscreen-loader">
        <div className="spinner-large" />
        <p>Loading your workspace...</p>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  const handleOpenSubmit = (task) => {
    setSelectedTask(task);
    setIsSubmitModalOpen(true);
  };

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  // Tab Header Details
  const getTabInfo = () => {
    switch (currentTab) {
      case 'dashboard':
        return {
          title: isEmployee && !isManager && !isAdmin ? 'Daily Workspace' : 'Executive Overview',
          subtitle: 'Daily task status and progress metrics',
        };
      case 'tasks':
        return {
          title: 'Task Deliverables',
          subtitle: 'Active assignments and target due dates',
        };
      case 'updates':
        return {
          title: 'Daily Progress Audit',
          subtitle: 'End-of-day submissions and developer remarks',
        };
      case 'reports':
        return {
          title: 'Analytics & Reports',
          subtitle: 'Aggregated completion and productivity statistics',
        };
      case 'users':
        return {
          title: 'Team Directory',
          subtitle: 'Organizational hierarchy and active team members',
        };
      default:
        return { title: 'Workspace', subtitle: '' };
    }
  };

  const tabInfo = getTabInfo();

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />

      {/* Main Content Area */}
      <div className="app-main">
        <Header
          title={tabInfo.title}
          subtitle={tabInfo.subtitle}
          onRefresh={handleRefresh}
        />

        <main className="app-content" key={refreshKey}>
          {currentTab === 'dashboard' && (
            <DashboardPage
              onOpenSubmitModal={handleOpenSubmit}
              onOpenCreateTaskModal={() => setIsCreateTaskModalOpen(true)}
            />
          )}

          {currentTab === 'tasks' && (
            <TasksPage
              onOpenSubmitModal={handleOpenSubmit}
              onOpenCreateTaskModal={() => setIsCreateTaskModalOpen(true)}
            />
          )}

          {currentTab === 'updates' && <DailyUpdatesPage />}

          {currentTab === 'reports' && (isAdmin || isManager) && <ReportsPage />}

          {currentTab === 'users' && (isAdmin || isManager) && (
            <UsersPage onOpenCreateUserModal={() => setIsCreateUserModalOpen(true)} />
          )}
        </main>
      </div>

      {/* Modals */}
      <SubmitDailyUpdateModal
        isOpen={isSubmitModalOpen}
        task={selectedTask}
        onClose={() => {
          setIsSubmitModalOpen(false);
          setSelectedTask(null);
        }}
        onSuccess={handleRefresh}
      />

      <CreateTaskModal
        isOpen={isCreateTaskModalOpen}
        onClose={() => setIsCreateTaskModalOpen(false)}
        onSuccess={handleRefresh}
      />

      <CreateUserModal
        isOpen={isCreateUserModalOpen}
        onClose={() => setIsCreateUserModalOpen(false)}
        onSuccess={handleRefresh}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

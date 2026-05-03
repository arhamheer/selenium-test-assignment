import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getProject,
  getTasks,
  getUsers,
  createTask,
  addProjectMember,
  removeProjectMember,
} from "../api/api";
import TaskCard from "./TaskCard";

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showMemberForm, setShowMemberForm] = useState(false);
  const [taskName, setTaskName] = useState("");
  const [taskDesc, setTaskDesc] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [newMemberId, setNewMemberId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // Get current user from token
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        // Store email from token to match with users
        sessionStorage.setItem("userEmail", payload.sub);
      } catch (e) {
        console.error("Failed to parse token");
      }
    }
    loadProjectData();
  }, [id]);

  const loadProjectData = async () => {
    try {
      const [projectData, tasksData, usersData] = await Promise.all([
        getProject(id),
        getTasks(id),
        getUsers(),
      ]);
      setProject(projectData);
      setTasks(tasksData);
      setUsers(usersData);

      // Find current user ID from users list
      const userEmail = sessionStorage.getItem("userEmail");
      const current = usersData.find((u) => u.email === userEmail);
      if (current) {
        setCurrentUserId(current.id);
      }

      setError("");
    } catch (err) {
      console.error("Error loading project:", err);
      setError("Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      await createTask({
        name: taskName,
        description: taskDesc,
        project_id: parseInt(id),
        assigned_to: assignedTo ? parseInt(assignedTo) : null,
        status: "to-do",
      });
      setTaskName("");
      setTaskDesc("");
      setAssignedTo("");
      setShowForm(false);
      loadProjectData();
    } catch (err) {
      console.error("Error creating task:", err);
      setError("Failed to create task");
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    try {
      await addProjectMember(parseInt(id), parseInt(newMemberId));
      setNewMemberId("");
      setShowMemberForm(false);
      setError("");
      loadProjectData();
    } catch (err) {
      console.error("Error adding member:", err);
      setError("Failed to add member. Make sure they're not already a member.");
    }
  };

  const handleRemoveMember = async (userId) => {
    if (confirm("Are you sure you want to remove this member?")) {
      try {
        await removeProjectMember(parseInt(id), userId);
        loadProjectData();
      } catch (err) {
        console.error("Error removing member:", err);
        setError("Failed to remove member");
      }
    }
  };

  const projectMembers = users.filter((u) => project?.members.includes(u.id));
  const assignableUsers = [
    users.find((u) => u.id === project?.owner_id),
    ...projectMembers,
  ].filter(Boolean); // Remove undefined/duplicates

  const availableUsers = users.filter(
    (u) => !project?.members.includes(u.id) && u.id !== project?.owner_id,
  );

  const tasksByStatus = {
    "to-do": tasks.filter((t) => t.status === "to-do"),
    "in-progress": tasks.filter((t) => t.status === "in-progress"),
    done: tasks.filter((t) => t.status === "done"),
  };

  if (loading) {
    return (
      <div
        className="flex justify-center items-center h-screen"
        data-testid="project-loading"
      >
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="project-detail-page">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate("/dashboard")}
                data-testid="back-button"
                className="text-blue-600 hover:text-blue-800 mr-4"
              >
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-gray-800">
                {project?.name}
              </h1>
            </div>
            {project?.owner_id === currentUserId && (
              <button
                onClick={() => setShowForm(!showForm)}
                data-testid="add-task-button"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm"
              >
                + Add Task
              </button>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-gray-600 mb-6">{project?.description}</p>

        {error && (
          <div
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
            data-testid="project-error"
          >
            {error}
          </div>
        )}

        {/* Members Section */}
        <div
          className="bg-white rounded-lg shadow p-6 mb-8"
          data-testid="members-section"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              Team Members ({projectMembers.length + 1})
            </h3>
            {project?.owner_id === currentUserId && (
              <button
                onClick={() => setShowMemberForm(!showMemberForm)}
                data-testid="add-member-button"
                className="bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 transition text-sm"
              >
                + Add Member
              </button>
            )}
          </div>

          {/* Member List */}
          <div className="space-y-2">
            {/* Show Owner */}
            {users.find((u) => u.id === project?.owner_id) && (
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <p className="font-medium text-gray-800">
                    {users.find((u) => u.id === project?.owner_id)?.name}
                  </p>
                  <p className="text-sm text-gray-600">
                    {users.find((u) => u.id === project?.owner_id)?.email}
                  </p>
                  <span className="text-xs text-blue-600 font-medium">
                    Owner
                  </span>
                </div>
              </div>
            )}

            {/* Show Members */}
            {projectMembers.length === 0 && !showMemberForm && (
              <p className="text-gray-500 text-sm">
                No members yet. Add your team!
              </p>
            )}
            {projectMembers.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-800">{member.name}</p>
                  <p className="text-sm text-gray-600">{member.email}</p>
                </div>
                {project?.owner_id === currentUserId && (
                  <button
                    onClick={() => handleRemoveMember(member.id)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Add Member Form */}
          {showMemberForm && (
            <form
              onSubmit={handleAddMember}
              className="mt-4 p-4 bg-gray-50 rounded-lg"
              data-testid="add-member-form"
            >
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select User
                </label>
                <select
                  value={newMemberId}
                  onChange={(e) => setNewMemberId(e.target.value)}
                  data-testid="member-select"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                >
                  <option value="">Choose a user...</option>
                  {availableUsers.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name} ({user.email})
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  data-testid="member-submit-button"
                  className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition text-sm"
                >
                  Add
                </button>
                <button
                  type="button"
                  onClick={() => setShowMemberForm(false)}
                  data-testid="member-cancel-button"
                  className="bg-gray-300 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-400 transition text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Task Form */}
        {showForm && (
          <div
            className="bg-white rounded-lg shadow p-6 mb-6"
            data-testid="task-form"
          >
            <h3 className="text-lg font-semibold mb-4">Create New Task</h3>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task Name
                </label>
                <input
                  type="text"
                  value={taskName}
                  onChange={(e) => setTaskName(e.target.value)}
                  data-testid="task-name-input"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                  data-testid="task-description-input"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assign To
                </label>
                <select
                  value={assignedTo}
                  onChange={(e) => setAssignedTo(e.target.value)}
                  data-testid="task-assignee-select"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Unassigned</option>
                  {assignableUsers.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  data-testid="task-create-button"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  data-testid="task-cancel-button"
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-4" data-testid="todo-column">
            <div className="bg-gray-100 px-4 py-2 rounded-lg">
              <h3 className="font-semibold text-gray-700">To Do</h3>
              <span className="text-sm text-gray-500">
                {tasksByStatus["to-do"].length} tasks
              </span>
            </div>
            {tasksByStatus["to-do"].map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                users={users}
                onUpdate={loadProjectData}
                currentUserId={currentUserId}
                projectOwnerId={project?.owner_id}
                projectMembers={project?.members}
              />
            ))}
          </div>

          <div className="space-y-4" data-testid="in-progress-column">
            <div className="bg-blue-100 px-4 py-2 rounded-lg">
              <h3 className="font-semibold text-blue-700">In Progress</h3>
              <span className="text-sm text-blue-600">
                {tasksByStatus["in-progress"].length} tasks
              </span>
            </div>
            {tasksByStatus["in-progress"].map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                users={users}
                onUpdate={loadProjectData}
                currentUserId={currentUserId}
                projectOwnerId={project?.owner_id}
                projectMembers={project?.members}
              />
            ))}
          </div>

          <div className="space-y-4" data-testid="done-column">
            <div className="bg-green-100 px-4 py-2 rounded-lg">
              <h3 className="font-semibold text-green-700">Done</h3>
              <span className="text-sm text-green-600">
                {tasksByStatus["done"].length} tasks
              </span>
            </div>
            {tasksByStatus["done"].map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                users={users}
                onUpdate={loadProjectData}
                currentUserId={currentUserId}
                projectOwnerId={project?.owner_id}
                projectMembers={project?.members}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createProject, getUsers } from "../api/api";

export default function ProjectList({ projects, onProjectsChange }) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [currentUserId, setCurrentUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Get current user from token
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        sessionStorage.setItem("userEmail", payload.sub);

        // Fetch users to find current user ID
        getUsers().then((users) => {
          const current = users.find((u) => u.email === payload.sub);
          if (current) {
            setCurrentUserId(current.id);
          }
        });
      } catch (e) {
        console.error("Failed to parse token");
      }
    }
  }, []);

  const getUserRole = (project) => {
    if (project.owner_id === currentUserId) {
      return { role: "Owner", color: "bg-blue-100 text-blue-800" };
    } else if (project.members?.includes(currentUserId)) {
      return { role: "Member", color: "bg-green-100 text-green-800" };
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createProject({ name, description, members: [] });
      setName("");
      setDescription("");
      setShowForm(false);
      onProjectsChange();
    } catch (err) {
      console.error("Error creating project:", err);
    }
  };

  return (
    <div data-testid="project-list">
      <div className="flex justify-between items-center mb-6">
        <h2
          className="text-2xl font-bold text-gray-800"
          data-testid="projects-heading"
        >
          Projects
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          data-testid="new-project-button"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          + New Project
        </button>
      </div>

      {showForm && (
        <div
          className="bg-white rounded-lg shadow p-6 mb-6"
          data-testid="project-form"
        >
          <h3 className="text-lg font-semibold mb-4">Create New Project</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                data-testid="project-name-input"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                data-testid="project-description-input"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                data-testid="project-create-button"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                data-testid="project-cancel-button"
                className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => {
          const roleInfo = getUserRole(project);
          return (
            <div
              key={project.id}
              onClick={() => navigate(`/project/${project.id}`)}
              data-testid={`project-card-${project.id}`}
              className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer p-6"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-xl font-semibold text-gray-800">
                  {project.name}
                </h3>
                {roleInfo && (
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded ${roleInfo.color}`}
                  >
                    {roleInfo.role}
                  </span>
                )}
              </div>
              <p className="text-gray-600 text-sm mb-4">
                {project.description || "No description"}
              </p>
              <div className="flex items-center text-sm text-gray-500">
                <svg
                  className="w-4 h-4 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
                {project.members?.length || 0} members
              </div>
            </div>
          );
        })}
      </div>

      {projects.length === 0 && !showForm && (
        <div
          className="text-center py-12 text-gray-500"
          data-testid="empty-project-state"
        >
          No projects yet. Create your first project to get started!
        </div>
      )}
    </div>
  );
}

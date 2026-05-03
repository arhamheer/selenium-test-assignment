const API_URL = "http://localhost:8000";

const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Auth
export const login = async (email, password) => {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Login failed");
  return response.json();
};

export const createUser = async (userData) => {
  const response = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  if (!response.ok) throw new Error("User creation failed");
  return response.json();
};

// Users
export const getUsers = async () => {
  const response = await fetch(`${API_URL}/users/`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error("Failed to fetch users");
  return response.json();
};

// Projects
export const getProjects = async () => {
  const response = await fetch(`${API_URL}/projects/`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error("Failed to fetch projects");
  return response.json();
};

export const getProject = async (id) => {
  const response = await fetch(`${API_URL}/projects/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error("Failed to fetch project");
  return response.json();
};

export const createProject = async (projectData) => {
  const response = await fetch(`${API_URL}/projects/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(projectData),
  });
  if (!response.ok) throw new Error("Failed to create project");
  return response.json();
};

export const addProjectMember = async (projectId, userId) => {
  const response = await fetch(
    `${API_URL}/projects/${projectId}/members/${userId}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );
  if (!response.ok) throw new Error("Failed to add member");
  return response.json();
};

export const removeProjectMember = async (projectId, userId) => {
  const response = await fetch(
    `${API_URL}/projects/${projectId}/members/${userId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );
  if (!response.ok) throw new Error("Failed to remove member");
  return response.json();
};

// Tasks
export const getTasks = async (projectId = null) => {
  const url = projectId
    ? `${API_URL}/tasks/?project_id=${projectId}`
    : `${API_URL}/tasks/`;
  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error("Failed to fetch tasks");
  return response.json();
};

export const createTask = async (taskData) => {
  const response = await fetch(`${API_URL}/tasks/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(taskData),
  });
  if (!response.ok) throw new Error("Failed to create task");
  return response.json();
};

export const updateTask = async (id, taskData) => {
  const response = await fetch(`${API_URL}/tasks/${id}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(taskData),
  });
  if (!response.ok) throw new Error("Failed to update task");
  return response.json();
};

export const deleteTask = async (id) => {
  const response = await fetch(`${API_URL}/tasks/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error("Failed to delete task");
  return response.json();
};

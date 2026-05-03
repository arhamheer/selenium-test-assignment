import { useState } from "react";
import { updateTask, deleteTask } from "../api/api";

export default function TaskCard({
  task,
  users,
  onUpdate,
  currentUserId,
  projectOwnerId,
  projectMembers,
}) {
  const [status, setStatus] = useState(task.status);
  const [assignedTo, setAssignedTo] = useState(task.assigned_to || "");

  const assignedUser = users.find((u) => u.id === task.assigned_to);
  const isMyTask = task.assigned_to === currentUserId;
  const isOwner = projectOwnerId === currentUserId;
  const canEdit = isMyTask || isOwner;

  // Only show project members and owner as assignable
  const assignableUsers = users.filter(
    (u) => u.id === projectOwnerId || projectMembers?.includes(u.id),
  );

  const handleStatusChange = async (newStatus) => {
    try {
      await updateTask(task.id, { status: newStatus });
      setStatus(newStatus);
      onUpdate();
    } catch (err) {
      console.error("Error updating task:", err);
    }
  };

  const handleAssigneeChange = async (newAssignedTo) => {
    try {
      const newValue = newAssignedTo ? parseInt(newAssignedTo) : null;
      await updateTask(task.id, { assigned_to: newValue });
      setAssignedTo(newValue || "");
      onUpdate();
    } catch (err) {
      console.error("Error updating assignee:", err);
    }
  };

  const handleDelete = async () => {
    if (window.confirm("Delete this task?")) {
      try {
        await deleteTask(task.id);
        onUpdate();
      } catch (err) {
        console.error("Error deleting task:", err);
      }
    }
  };

  const statusColors = {
    "to-do": "bg-gray-50 border-gray-200",
    "in-progress": "bg-blue-50 border-blue-200",
    done: "bg-green-50 border-green-200",
  };

  return (
    <div
      data-testid={`task-card-${task.id}`}
      className={`rounded-lg border-2 ${statusColors[status]} p-4 shadow-sm`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <h4 className="font-semibold text-gray-800">{task.name}</h4>
          {isMyTask && (
            <span className="text-xs font-semibold px-2 py-1 rounded bg-yellow-100 text-blue-800">
              My Task
            </span>
          )}
        </div>
        {canEdit && (
          <button
            onClick={handleDelete}
            data-testid="task-delete-button"
            className="text-red-500 hover:text-red-700 text-sm"
          >
            ✕
          </button>
        )}
      </div>

      {task.description && (
        <p className="text-sm text-gray-600 mb-3">{task.description}</p>
      )}

      <div className="space-y-2">
        {isOwner && (
          <select
            value={assignedTo}
            onChange={(e) => handleAssigneeChange(e.target.value)}
            data-testid="task-assignee-select"
            className="w-full text-sm px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Unassigned</option>
            {assignableUsers.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} ({user.email})
              </option>
            ))}
          </select>
        )}

        {!isOwner && assignedUser && (
          <div className="flex items-center text-sm text-gray-700">
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            {assignedUser.name}
          </div>
        )}

        {!isOwner && !assignedUser && (
          <div className="text-sm text-gray-500 italic">Unassigned</div>
        )}

        <select
          value={status}
          onChange={(e) => handleStatusChange(e.target.value)}
          disabled={!canEdit}
          data-testid="task-status-select"
          className={`w-full text-sm px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            !canEdit ? "bg-gray-100 cursor-not-allowed opacity-60" : ""
          }`}
        >
          <option value="to-do">To Do</option>
          <option value="in-progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>
    </div>
  );
}

import React from 'react';

function TodoItem({ todo, onToggle, onDelete }) {
  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''}`}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
        className="todo-checkbox"
        id={`todo-${todo.id}`}
      />
      <label 
        htmlFor={`todo-${todo.id}`}
        className="todo-text"
      >
        {todo.text}
      </label>
      <button
        onClick={() => onDelete(todo.id)}
        className="todo-delete"
        aria-label={`Delete todo: ${todo.text}`}
      >
        ×
      </button>
    </div>
  );
}

export default TodoItem;
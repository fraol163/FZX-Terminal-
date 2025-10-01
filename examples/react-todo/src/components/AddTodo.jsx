import React, { useState } from 'react';

function AddTodo({ onAdd }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      onAdd(text.trim());
      setText('');
    }
  };

  return (
    <form className="add-todo-form" onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a new todo..."
        className="add-todo-input"
        autoComplete="off"
      />
      <button 
        type="submit" 
        className="add-todo-button"
        disabled={!text.trim()}
      >
        Add
      </button>
    </form>
  );
}

export default AddTodo;
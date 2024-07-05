import React, { useState } from 'react';
import './App.css';

function App() {
  const [todos, setTodos] = useState([
    { text: 'Instant Coffee Pack', completed: false },
    { text: 'Apples', completed: false },
  ]);
  const [newTodo, setNewTodo] = useState('');
  const [notificationOption, setNotificationOption] = useState('Always notify me');
  const [imageFile, setImageFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');

  const addTodo = () => {
    if (newTodo.trim() !== '') {
      setTodos([...todos, { text: newTodo, completed: false }]);
      setNewTodo('');
    }
  };

  const toggleTodo = index => {
    const newTodos = [...todos];
    newTodos[index].completed = !newTodos[index].completed;
    setTodos(newTodos);
  };

  const handleNotificationChange = (event) => {
    setNotificationOption(event.target.value);
    alert(`Notification option set to: ${event.target.value}`);
  };

  const handleFileChange = (event) => {
    setImageFile(event.target.files[0]);
  };

  const handleScanClick = async () => {
    if (!imageFile) {
      alert('Please select an image file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', imageFile);

    try {
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      if (response.ok) {
        setExtractedText(result.text);
        alert('Text extracted: ' + result.text);
      } else {
        alert('Error: ' + result.error);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const mockData = [
    { name: 'Apple', price: '$1.95', location: 'Coles' },
    { name: 'Coffee', price: '$5.10', location: 'Aldi' },
    { name: 'Banana', price: '$2.99', location: 'Woolies' },
    { name: 'Shampoo', price: '$4.69', location: 'Aldi' },
  ];

  return (
    <div className="App">
      <header className="App-header">
        <div className="button-container">
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button className="custom-button" onClick={handleScanClick}>Camera Scan</button>
          <div className="dropdown">
            <button className="custom-button">Notifications</button>
            <div className="dropdown-content">
              <select value={notificationOption} onChange={handleNotificationChange}>
                <option value="Always notify me">Always notify me</option>
                <option value="Notify me until marked off">Notify me until marked off</option>
              </select>
            </div>
          </div>
        </div>
        <div className="table-container">
          <h2>Items List</h2>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              {mockData.map((item, index) => (
                <tr key={index}>
                  <td>{item.name}</td>
                  <td>{item.price}</td>
                  <td>{item.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="todo-container">
          <h2>To Buy List</h2>
          <div className="todo-input">
            <input
              type="text"
              value={newTodo}
              onChange={e => setNewTodo(e.target.value)}
              placeholder="What would you like to buy"
            />
            <button className="add-button" onClick={addTodo}>Add</button>
          </div>
          <ul className="todo-list">
            {todos.map((todo, index) => (
              <li key={index} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => toggleTodo(index)}
                />
                <span>{todo.text}</span>
              </li>
            ))}
          </ul>
        </div>
        {extractedText && (
          <div className="extracted-text-container">
            <h2>Extracted Text</h2>
            <p>{extractedText}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;

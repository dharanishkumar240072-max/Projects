import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [students, setStudents] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = () => {
    fetch("http://localhost:8080/students")
      .then((res) => res.json())
      .then((data) => setStudents(data));
  };

  // Validation
  const validate = () => {
    let newErrors = {};

    // Name — only letters
    if (!name.match(/^[a-zA-Z ]+$/)) {
      newErrors.name = "Name must contain only letters!";
    }

    // Email — must have @ and .com
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = "Enter a valid email like abc@gmail.com";
    }

    // Password — exactly 6 characters
    if (password.length !== 6) {
      newErrors.password = "Password must be exactly 6 characters!";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const saveStudent = () => {
    if (!validate()) return;

    fetch("http://localhost:8080/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, email: email }),
    })
      .then((res) => res.json())
      .then(() => {
        fetchStudents();
        setName("");
        setEmail("");
        setPassword("");
        setErrors({});
      });
  };

  return (
    <div className="container">
      <h1 className="title">🎓 Student App</h1>

      {/* Add Student Form */}
      <div className="form-card">
        <h2>Add Student</h2>

        {/* Name */}
        <input
          className="input"
          type="text"
          placeholder="Enter Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {errors.name && <p className="error">{errors.name}</p>}

        {/* Email */}
        <input
          className="input"
          type="email"
          placeholder="Enter Email (abc@gmail.com)"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        {errors.email && <p className="error">{errors.email}</p>}

        {/* Password */}
        <input
          className="input"
          type="password"
          placeholder="Enter Password (6 characters)"
          value={password}
          maxLength={6}
          onChange={(e) => setPassword(e.target.value)}
        />
        {errors.password && <p className="error">{errors.password}</p>}

        <button className="btn" onClick={saveStudent}>
          Add Student
        </button>
      </div>

      {/* Student List */}
      <div className="list-section">
        <h2>Student List</h2>
        {students.length === 0 ? (
          <p className="empty">No students found!</p>
        ) : (
          students.map((s) => (
            <div className="student-card" key={s.id}>
              <h3>👤 {s.name}</h3>
              <p>📧 {s.email}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
import React, { useEffect, useState } from "react";

function TrialPrepSchoolSection() {
  const [lessons, setLessons] = useState([]);

  useEffect(() => {
    fetch("/api/lessons")
      .then((r) => r.json())
      .then(setLessons)
      .catch(() => setLessons([]));
  }, []);

  const markComplete = (id) => {
    fetch(`/api/lessons/${id}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: true }),
    })
      .then((r) => r.json())
      .then((data) => {
        setLessons((ls) =>
          ls.map((l) => (l.id === id ? { ...l, progress: [data] } : l))
        );
      });
  };

  return (
    <div className="card-grid">
      {lessons.map((lesson) => (
        <div key={lesson.id} className="card">
          <h3>{lesson.title}</h3>
          <p>{lesson.summary}</p>
          {lesson.progress && lesson.progress[0] && lesson.progress[0].completed ? (
            <span className="badge">Completed</span>
          ) : (
            <button onClick={() => markComplete(lesson.id)}>Mark Complete</button>
          )}
        </div>
      ))}
    </div>
  );
}

export default TrialPrepSchoolSection;

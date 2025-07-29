import React, { useState, useEffect } from "react";
function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  useEffect(() => {
    const socket = io('/chat');
    socket.on('update_speech', d => setMessages(m => [...m, {type:'speech', text:d.data}]));
    socket.on('update_user_input', d => setMessages(m => [...m, {type:'user', text:d.data}]));
    return () => socket.disconnect();
  }, []);
  const send = () => {
    if (!input.trim()) return;
    fetch('/api/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text: input})})
      .then(() => setInput(''));
  };
  return (
    <section className="card">
      <h2>Chat</h2>
      <div className="chat-box" style={{maxHeight:'160px'}}>
        {messages.map((m,i) => <div key={i} className={m.type==='user'?'user-msg':'speech-msg'}>{m.text}</div>)}
      </div>
      <textarea value={input} onChange={e=>setInput(e.target.value)} rows="2" className="w-full mb-2 p-2 rounded" placeholder="Ask the assistant..."></textarea>
      <button className="button-primary" onClick={send}>Send</button>
    </section>
  );
}
export default ChatSection;

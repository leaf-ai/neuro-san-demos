import React, { useState, useEffect, useRef } from "react";
function SettingsModal({open,onClose}) {
  const [form,setForm] = useState({});
  const ref = useRef();
  useEffect(() => {
    if(open) {
      Promise.all([
        fetch('/api/settings').then(r=>r.json()),
        fetch('/api/feature-flags').then(r=>r.json())
      ]).then(([settings, flags]) => setForm({...settings, ...flags}));
    }
  }, [open]);
  const update = e => {
    const { name, type, checked, value } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };
  const submit = e => {
    e.preventDefault();
    const { voice_stt, voice_tts, voice_commands, theories, binder, chat, ...rest } = form;
    const flags = { voice_stt, voice_tts, voice_commands, theories, binder, chat };
    Promise.all([
      fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(rest)}),
      fetch('/api/feature-flags',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(flags)})
    ]).then(()=>onClose());
  };
  if(!open) return null;
  return (
    <div className="modal" onClick={e=>{if(e.target===ref.current) onClose();}} ref={ref}>
      <div className="modal-content">
        <span className="close-btn" onClick={onClose}>&times;</span>
        <h2>API Settings</h2>
        <form id="settings-form" onSubmit={submit} className="space-y-2 overflow-y-auto" style={{maxHeight:'60vh'}}>
          <label>CourtListener API Key<input type="text" name="courtlistener_api_key" value={form.courtlistener_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>CourtListener Endpoint<input type="text" name="courtlistener_com_api_endpoint" value={form.courtlistener_com_api_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>California Codes URL<input type="text" name="california_codes_url" value={form.california_codes_url||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Gemini API Key<input type="text" name="gemini_api_key" value={form.gemini_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Google API Endpoint<input type="text" name="google_api_endpoint" value={form.google_api_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>VerifyPDF API Key<input type="text" name="verifypdf_api_key" value={form.verifypdf_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>VerifyPDF Endpoint<input type="text" name="verify_pdf_endpoint" value={form.verify_pdf_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Riza Key<input type="text" name="riza_key" value={form.riza_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j URI<input type="text" name="neo4j_uri" value={form.neo4j_uri||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Username<input type="text" name="neo4j_username" value={form.neo4j_username||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Password<input type="password" name="neo4j_password" value={form.neo4j_password||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Database<input type="text" name="neo4j_database" value={form.neo4j_database||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Aura Instance ID<input type="text" name="aura_instance_id" value={form.aura_instance_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Aura Instance Name<input type="text" name="aura_instance_name" value={form.aura_instance_name||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Project ID<input type="text" name="gcp_project_id" value={form.gcp_project_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Vertex Data Store<input type="text" name="gcp_vertex_ai_data_store_id" value={form.gcp_vertex_ai_data_store_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Search App<input type="text" name="gcp_vertex_ai_search_app" value={form.gcp_vertex_ai_search_app||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Service Account Key<textarea name="gcp_service_account_key" value={form.gcp_service_account_key||''} onChange={update} className="w-full p-2 rounded" rows="2"/></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="theories" checked={form.theories||false} onChange={update}/><span>Enable Legal Theories</span></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="binder" checked={form.binder||false} onChange={update}/><span>Enable Binder</span></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="chat" checked={form.chat||false} onChange={update}/><span>Enable Chat</span></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="voice_stt" checked={form.voice_stt||false} onChange={update}/><span>Enable Voice Transcription</span></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="voice_tts" checked={form.voice_tts||false} onChange={update}/><span>Enable Voice Synthesis</span></label>
          <label className="flex items-center space-x-2"><input type="checkbox" name="voice_commands" checked={form.voice_commands||false} onChange={update}/><span>Enable Voice Commands</span></label>
          <button className="button-primary" type="submit">Save</button>
        </form>
      </div>
    </div>
  );
}

export default SettingsModal;

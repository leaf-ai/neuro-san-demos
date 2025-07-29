import React, { useState, useEffect } from "react";
import ChatSection from "./components/ChatSection";
import StatsSection from "./components/StatsSection";
import PipelineSection from "./components/PipelineSection";
import OverviewSection from "./components/OverviewSection";
import UploadSection from "./components/UploadSection";
import TimelineSection from "./components/TimelineSection";
import GraphSection from "./components/GraphSection";
import DocToolsSection from "./components/DocToolsSection";
import ForensicSection from "./components/ForensicSection";
import VectorSection from "./components/VectorSection";
import TasksSection from "./components/TasksSection";
import CaseManagementSection from "./components/CaseManagementSection";
import ResearchSection from "./components/ResearchSection";
import SubpoenaSection from "./components/SubpoenaSection";
import PresentationSection from "./components/PresentationSection";
import SettingsModal from "./components/SettingsModal";
function Dashboard() {
  const [tab, setTab] = useState('overview');
  const [showSettings,setShowSettings] = useState(false);
  useEffect(()=>{
    const btn=document.getElementById('settings-btn');
    if(btn) btn.onclick=()=>setShowSettings(true);
  },[]);
  return (
    <div>
      <div className="tab-buttons">
        {['overview','pipeline','chat','stats','upload','timeline','graph','docs','forensic','vector','tasks','case','research','subpoena','presentation'].map(t => (
          <button key={t} className={`tab-button ${tab===t?'active':''}`} onClick={()=>setTab(t)} data-target={`tab-${t}`}>{t.charAt(0).toUpperCase()+t.slice(1)}</button>
        ))}
      </div>
      <div className="tab-content" style={{display: tab==='overview'?'block':'none'}}><OverviewSection/></div>
      <div className="tab-content" style={{display: tab==='pipeline'?'block':'none'}}><PipelineSection/></div>
      <div className="tab-content" style={{display: tab==='chat'?'block':'none'}}><ChatSection/></div>
      <div className="tab-content" style={{display: tab==='stats'?'block':'none'}}><StatsSection/></div>
      <div className="tab-content" style={{display: tab==='upload'?'block':'none'}}><UploadSection/></div>
      <div className="tab-content" style={{display: tab==='timeline'?'block':'none'}}><TimelineSection/></div>
      <div className="tab-content" style={{display: tab==='graph'?'block':'none'}}><GraphSection/></div>
      <div className="tab-content" style={{display: tab==='docs'?'block':'none'}}><DocToolsSection/></div>
      <div className="tab-content" style={{display: tab==='forensic'?'block':'none'}}><ForensicSection/></div>
      <div className="tab-content" style={{display: tab==='vector'?'block':'none'}}><VectorSection/></div>
      <div className="tab-content" style={{display: tab==='tasks'?'block':'none'}}><TasksSection/></div>
      <div className="tab-content" style={{display: tab==='case'?'block':'none'}}><CaseManagementSection/></div>
      <div className="tab-content" style={{display: tab==='research'?'block':'none'}}><ResearchSection/></div>
      <div className="tab-content" style={{display: tab==='subpoena'?'block':'none'}}><SubpoenaSection/></div>
      <div className="tab-content" style={{display: tab==='presentation'?'block':'none'}}><PresentationSection/></div>
      <SettingsModal open={showSettings} onClose={()=>setShowSettings(false)}/>
    </div>
  );
}

export default Dashboard;

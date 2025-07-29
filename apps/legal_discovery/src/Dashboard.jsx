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
const TABS = [
  {id:'overview', label:'Overview', icon:'fa-home'},
  {id:'pipeline', label:'Team Pipeline', icon:'fa-route'},
  {id:'chat', label:'Orchestrator', icon:'fa-comments'},
  {id:'stats', label:'Stats', icon:'fa-chart-bar'},
  {id:'upload', label:'Ingestion', icon:'fa-upload'},
  {id:'timeline', label:'Timeline', icon:'fa-clock'},
  {id:'graph', label:'Graph', icon:'fa-project-diagram'},
  {id:'docs', label:'Discovery Tools', icon:'fa-file-alt'},
  {id:'forensic', label:'Forensics', icon:'fa-search-dollar'},
  {id:'vector', label:'Vector DB', icon:'fa-database'},
  {id:'tasks', label:'Scheduling', icon:'fa-tasks'},
  {id:'case', label:'Case Mgmt', icon:'fa-folder-open'},
  {id:'research', label:'Legal Research', icon:'fa-book-open'},
  {id:'subpoena', label:'Subpoena', icon:'fa-gavel'},
  {id:'presentation', label:'Trial Prep', icon:'fa-slideshare'},
  {id:'pipeline', label:'Pipeline', icon:'fa-route'},
  {id:'chat', label:'Chat', icon:'fa-comments'},
  {id:'stats', label:'Stats', icon:'fa-chart-bar'},
  {id:'upload', label:'Upload', icon:'fa-upload'},
  {id:'timeline', label:'Timeline', icon:'fa-clock'},
  {id:'graph', label:'Graph', icon:'fa-project-diagram'},
  {id:'docs', label:'Docs', icon:'fa-file-alt'},
  {id:'forensic', label:'Forensic', icon:'fa-search-dollar'},
  {id:'vector', label:'Vector', icon:'fa-database'},
  {id:'tasks', label:'Tasks', icon:'fa-tasks'},
  {id:'case', label:'Case', icon:'fa-folder-open'},
  {id:'research', label:'Research', icon:'fa-book-open'},
  {id:'subpoena', label:'Subpoena', icon:'fa-gavel'},
  {id:'presentation', label:'Presentation', icon:'fa-slideshare'}
];

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
        {TABS.map(t => (
          <button key={t.id} className={`tab-button ${tab===t.id?'active':''}`} onClick={()=>setTab(t.id)} data-target={`tab-${t.id}`}
            title={t.label}>
            <i className={`fa ${t.icon} mr-1`}></i>{t.label}
          </button>
        ))}
      </div>
      <div className="tab-content" style={{display: tab==='overview'?'block':'none'}} id="tab-overview"><OverviewSection/></div>
      <div className="tab-content" style={{display: tab==='pipeline'?'block':'none'}} id="tab-pipeline"><PipelineSection/></div>
      <div className="tab-content" style={{display: tab==='chat'?'block':'none'}} id="tab-chat"><ChatSection/></div>
      <div className="tab-content" style={{display: tab==='stats'?'block':'none'}} id="tab-stats"><StatsSection/></div>
      <div className="tab-content" style={{display: tab==='upload'?'block':'none'}} id="tab-upload"><UploadSection/></div>
      <div className="tab-content" style={{display: tab==='timeline'?'block':'none'}} id="tab-timeline"><TimelineSection/></div>
      <div className="tab-content" style={{display: tab==='graph'?'block':'none'}} id="tab-graph"><GraphSection/></div>
      <div className="tab-content" style={{display: tab==='docs'?'block':'none'}} id="tab-docs"><DocToolsSection/></div>
      <div className="tab-content" style={{display: tab==='forensic'?'block':'none'}} id="tab-forensic"><ForensicSection/></div>
      <div className="tab-content" style={{display: tab==='vector'?'block':'none'}} id="tab-vector"><VectorSection/></div>
      <div className="tab-content" style={{display: tab==='tasks'?'block':'none'}} id="tab-tasks"><TasksSection/></div>
      <div className="tab-content" style={{display: tab==='case'?'block':'none'}} id="tab-case"><CaseManagementSection/></div>
      <div className="tab-content" style={{display: tab==='research'?'block':'none'}} id="tab-research"><ResearchSection/></div>
      <div className="tab-content" style={{display: tab==='subpoena'?'block':'none'}} id="tab-subpoena"><SubpoenaSection/></div>
      <div className="tab-content" style={{display: tab==='presentation'?'block':'none'}} id="tab-presentation"><PresentationSection/></div>
      <SettingsModal open={showSettings} onClose={()=>setShowSettings(false)}/>
    </div>
  );
}

export default Dashboard;
import React from "react";

const AGENT_NETWORK_DATA = [
  {
    name: 'Document Ingestion Team',
    description: 'Manages the intake and processing of legal documents.',
    tools: [
      { name: 'DataCollection', description: 'Ingests and processes a batch of documents.' },
      { name: 'VectorDatabaseManager', description: 'Manages the vector database for document search.' },
      { name: 'DocumentProcessor', description: 'Processes and prepares documents for analysis.' }
    ]
  },
  {
    name: 'Forensic Document Analysis Team',
    description: 'Analyzes documents for forensic evidence.',
    tools: [
      { name: 'FraudDetector', description: 'Identifies potential fraud within financial documents.' },
      { name: 'GraphAnalyzer', description: 'Builds a knowledge graph from document relationships.' }
    ]
  },
  {
    name: 'Legal Analysis Case Strategy Team',
    description: 'Provides legal analysis and case strategy recommendations.',
    tools: [
      { name: 'LegalSummary', description: 'Generates a summary of key legal arguments.' },
      { name: 'KnowledgeGraphManager', description: 'Manages and queries the legal knowledge graph.' }
    ]
  },
  {
    name: 'Timeline Construction Team',
    description: 'Constructs chronological timelines of events from case data.',
    tools: [
      { name: 'TimelineManager', description: 'Creates, updates, and exports case timelines.' }
    ]
  },
  {
    name: 'Legal Research Team',
    description: 'Conducts research on relevant legal precedents and references.',
    tools: [
      { name: 'ResearchTools', description: 'Performs legal and factual research.' }
    ]
  },
  {
    name: 'Forensic Financial Analysis Team',
    description: 'Analyzes financial data for irregularities and patterns.',
    tools: [
      { name: 'ForensicTools', description: 'Performs in-depth forensic analysis on financial records.' }
    ]
  },
  {
    name: 'Software Development Team',
    description: 'Builds and maintains the software tools for the agent network.',
    tools: [
      { name: 'CodeEditor', description: 'Provides a text editor for writing and modifying code.' },
      { name: 'FileManager', description: 'Manages files and directories on the system.' }
    ]
  },
  {
    name: 'Trial Preparation & Presentation Team',
    description: 'Prepares legal arguments and presentations for trial.',
    tools: [
      { name: 'PresentationGenerator', description: 'Creates and formats legal presentations.' },
      { name: 'SubpoenaManager', description: 'Manages the issuance and tracking of subpoenas.' },
      { name: 'DocumentModifier', description: 'Modifies and formats legal documents.' }
    ]
  }
];

function AgentNetworkSection() {
  return (
    <section className="card">
      <h2>Agent Network</h2>
      <div className="network-grid">
        {AGENT_NETWORK_DATA.map(team => (
          <div key={team.name} className="network-card">
            <h3>{team.name}</h3>
            <p className="mb-2 text-sm">{team.description}</p>
            <ul className="pl-4 text-sm">
              {team.tools.map(tool => (
                <li key={tool.name}>{tool.name} - {tool.description}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

export default AgentNetworkSection;

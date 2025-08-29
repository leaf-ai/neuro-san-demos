Param(
  [string]$Token = $env:GITHUB_TOKEN,
  [string]$Repo = 'ahouse2/neuro-san-studio-2',
  [string]$Head = 'feat/m3-graph-causation-deltas',
  [string]$Base = 'main'
)

$ErrorActionPreference = 'Stop'
if (-not $Token) { throw 'Provide -Token or set $env:GITHUB_TOKEN' }
$headers = @{ Authorization = "token $Token"; 'User-Agent'='codex-cli' }

$body = @'
Title: Legal Discovery: Graph Enrichment, Orchestrator Passes, Voice Settings, Graph/UI Controls, Setup Scripts

Overview:
- Elevates Legal Discovery with graph enrichment (causation/timeline), auto-orchestrated 3-pass analysis after ingestion, voice engine/model settings, Graph UI controls (sync/enrich/analyze, path tracing), and a live Pipeline view with pass details. Adds setup scripts and a PRP “restart” note for quick resumption.

What’s Included:
- Graph Enrichment:
  - Relations: CAUSES (Facts and TimelineEvents), OCCURS_BEFORE chains, SAME_TRANSACTION proximity; plus RELATED_TO, CO_SUPPORTS, TEMPORALLY_NEAR, EVIDENCES preserved.
  - Endpoints:
    - POST /api/graph/sync_timeline → upserts SQL timeline to Neo4j and stitches consecutive edges.
    - POST /api/graph/enrich → runs enrichment passes, returns per-relationship deltas.
    - GET /api/graph/analyze → returns centrality and meta.timeline (max chain length, 3-hop sequences).
- Orchestrator (3 Passes):
  - Auto-trigger on ingestion completion: run_case_analysis(case_id, iterations=3).
  - Each pass: enrichment + timeline metrics + theory suggestions + forensics status.
  - Shared findings: Redis MessageBus (RESEARCH_INSIGHT_TOPIC, TIMELINE_ALERT_TOPIC) + Socket.IO pipeline_pass events for UI.
- Voice Settings:
  - DB fields: voice_engine, voice_model.
  - Endpoints: GET /api/chat/voices, POST /api/chat/voice/settings.
  - Settings modal UI: engine/model selectors + “List Voices”.
- Graph UI:
  - Controls: Analyze, Sync Timeline, Enrich Graph.
  - Styling: edge types/widths, legend; CAUSES path tracing (node click picker + Trace Path UI).
- Pipeline UI:
  - Live listener for pipeline_pass; “Recent Analysis Passes” cards.
  - “Details” modal per pass: Graph Deltas, Timeline, Theories, Raw JSON.
- DevOps:
  - scripts/setup.ps1 (Windows) and scripts/setup.sh (macOS/Linux) for venv, Vite build, Docker compose (with Clean option on Windows).
  - Build fixes: tokens.css added; vis-timeline CSS/JS linked; duplicate hoverRef removed.
- PRP Memory:
  - docs/prps/legal_discovery_memory.md and docs/prps/prp_restart_entry.md (restart context with setup, checks, and next steps).

How to Validate:
- Setup (Windows): powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Clean
- App: http://localhost:8080
- Graph tab: Sync Timeline → Enrich Graph → Analyze; trace a CAUSES path via node clicks and Trace Path inputs; Clear to reset.
- Pipeline tab: watch “Recent Analysis Passes”; open “Details”.
- Settings: “List Voices” and set engine/model; verify GET/POST voice endpoints.

Quick Restart Context:
- See docs/prps/prp_restart_entry.md for a concise state/roadmap checkpoint.

Notes:
- tools/prps-codex is ignored locally; canonical PRP memory is under docs/prps/.
- Graph/Vector services are optional in dev; endpoints no-op gracefully when offline.

Next (post-PR):
- Tabs in Details modal (Deltas | Timeline | Theories | Raw), tooltips and edge weight hints, path export/share, and persistence of pass summaries in DB.
'@

# Find existing open PR from ahouse2:Head
$listUrl = "https://api.github.com/repos/$Repo/pulls?state=open&head=ahouse2:$Head"
try { $prs = Invoke-RestMethod -Headers $headers -Uri $listUrl -Method Get } catch { $prs = @() }
if ($prs -and $prs.Count -gt 0) {
  $pr = $prs[0]
  $patchUrl = "https://api.github.com/repos/$Repo/pulls/$($pr.number)"
  $payload = @{ body = $body } | ConvertTo-Json -Depth 5
  $res = Invoke-RestMethod -Headers $headers -Uri $patchUrl -Method Patch -Body $payload -ContentType 'application/json'
  Write-Output ("Updated PR #{0}: {1}" -f $res.number,$res.html_url)
} else {
  $createUrl = "https://api.github.com/repos/$Repo/pulls"
  $payload = @{ title = 'Legal Discovery: Graph Enrichment, Orchestrator Passes, Voice Settings, Graph/UI Controls, Setup Scripts'; head = $Head; base = $Base; body = $body } | ConvertTo-Json -Depth 5
  $res = Invoke-RestMethod -Headers $headers -Uri $createUrl -Method Post -Body $payload -ContentType 'application/json'
  Write-Output ("Created PR #{0}: {1}" -f $res.number,$res.html_url)
}


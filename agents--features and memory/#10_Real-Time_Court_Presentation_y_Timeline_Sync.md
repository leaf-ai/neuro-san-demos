## Real-Time Court Presentation & Timeline Sync

### Document Viewer with Deep Links
- React + PDF.js (or react-pdf) supporting page navigation, text selection, and highlights.
- Deep link format: `/viewer/resource_id=offer_of_proof`.
- Bookmarking: store user-specific positions and notes via `/api/bookmarks`; persisted in `user_resources`.

### Presentation Command Bus
- WebSocket channel (Flask-SocketIO or Supabase Realtime) broadcasting commands: `goto_page`, `zoom`, `highlight`, `play_media`.
- Roles: Presenter (full controls) vs. Viewer (read-only).
- URL structure: `/present/:mode/:doc_id`.

### Timeline Integration
- Timeline events (exhibit introductions, testimony segments) mapped to document pages.
- Clicking an event sends `goto_page` to all connected views and highlights the active segment.
- Transcript linkage: transcripts display in sync with viewer page for judges and jury displays.

### Distribution & Offline Use
- Presentation package export (HTML + assets) for USB/email sharing; auto-launches in offline mode.
- Optional quick-share QR code or link for courtroom devices.

### Crosslink & Annotation
- "Learn more" tooltips trigger related rule lookup in the knowledge base and open in a side pane.
- Annotations stored per user or per case; exportable with exhibits.

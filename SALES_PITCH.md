# DisplayAds Sales Pitch

Audience: Sales team pitching to multi-store franchise and retail groups who need consistent, centrally managed in-store digital signage integrated with their POS.

Elevator pitch
- Replace paper posters with centrally managed digital screens. One update, all stores, instantly. No couriers. No misprints. No delays.
- Purpose-built for franchises: enforce brand consistency, schedule promos by region or store type, and measure results.
- Plug-and-play devices activate via QR code. Your team scans once from the POS/manager app; the screen is live in under a minute.

Why we win vs. “that new tool”
- Franchise-first architecture: campaigns, media, and schedules cascade across locations with guardrails, not chaos.
- POS-native control: managers trigger or pause campaigns inside the POS—no extra logins or browser tabs during rush hour.
- Bulletproof rollout: devices pair with QR, auto-report health, and can be repointed to new servers/IPs without reflashing.
- Operational savings: eliminate print runs, shipping, and in-store manual swaps. Update pricing or legal quickly across all stores.
- Transparent analytics: impressions and uptime, per-screen and per-campaign, for ROI conversations with finance.

Core capabilities (what we demo)
- Central management
  - Create/edit campaigns with names, descriptions, screen orientation, and normalization rules.
  - Upload images/videos once; assign across stores or groups. Playlist order and per-asset durations.
  - Schedule by time of day, weekday, or season; default campaign fallback for off-hours.
- Device onboarding in 60 seconds
  - TV app shows a QR code with a unique activation code.
  - Manager mobile app scans the QR and assigns a name/location and default campaign.
  - Device starts pulling the assigned campaign and reports health/heartbeats automatically.
- Orientation & consistency
  - Campaign-level screen orientation (portrait/landscape) with optional auto-normalization to avoid stretched media.
  - Same creative, same playback order and durations across all stores—no “store-by-store drift.”
- Runtime flexibility for IT
  - Change the backend server URL at runtime on both TV and Manager apps—no rebuilds. Ideal for static IP moves or new regions.
  - Dockerized backend for quick deployments on Windows or Ubuntu.
- Analytics that matter
  - Heartbeats and impression logging at the device level.
  - Per-campaign metrics to see which promos play and where.

Security and control
- JWT-based authentication with role-aware APIs.
- Device activation codes expire and are single-use; blocked devices cannot rejoin without approval.
- Media storage via object storage with secure URL handling.

Implementation plan (what happens after PO)
- Week 1: Provision Docker stack; connect to your domain/IP; whitelist Manager app; pilot 2–3 stores.
- Week 2: Creative migration and campaign mapping by region/store type; train managers on the POS tab.
- Week 3–4: Roll out to remaining stores; enable analytics dashboards for weekly ops and marketing.

Proof points and objections handling
- “We need consistency across 50+ locations.” Our cascade model ensures a single source of truth; screens self-heal to the assigned campaign.
- “IT changes IPs sometimes.” Both apps support runtime base URL changes—no device swaps.
- “We’re worried about training.” Activation is QR-based; daily tasks live inside the POS where staff already work.
- “What about large video files?” Assets are streamed with caching; orientation rules prevent stretched or cropped content.

Packaging and pricing (example)
- SaaS per-screen monthly with volume tiers (e.g., 1–25, 26–100, 101+). Includes hosting, updates, and support.
- Optional: On-prem support package for self-hosted Docker deployments.
- Implementation bundle: onboarding, creative setup, and staff training.

Call to action
- Pick 3 pilot stores. We’ll activate them in under an hour and show you live, synchronized promos—no print, no waiting.

Appendix: Feature checklist for the demo
- Dashboard: create/edit campaigns; set orientation; upload media; order playlist; assign default campaigns to displays.
- TV app: shows QR for activation; plays assigned campaign; sends heartbeats; logs impressions.
- Manager app: QR scanner to activate displays; Settings screen to change server URL and test connectivity.
- Backend: Django + DRF; device activation endpoints; analytics endpoints; Docker deployment for Windows/Ubuntu.

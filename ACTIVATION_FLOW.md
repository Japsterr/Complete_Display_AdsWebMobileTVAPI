# Activation Flow and Rate Limiting

This document explains the Stage 2 changes to the device activation flow.

## Summary
- Activation codes expire after 15 minutes (900 seconds).
- If a pending device’s code is missing or expired, a new unique 6‑char code is generated.
- Endpoints are throttled to prevent abuse.
- Device campaign payload now includes a normalize_to_orientation hint.

## Endpoints
- POST /api/v1/devices/request-activation/
  - Body: { "device_id": "string", "device_info": { ... } }
  - Returns: activation_code, activation_url, activation_qr_png_base64, expires_in_seconds
  - Throttling: anonymous 20/min, authenticated 60/min

- POST /api/v1/devices/activate/
  - Auth required (JWT)
  - Body: { "activation_code": "ABC123", "display_name": "TV", "location": "Lobby" }
  - Validates TTL (15 min). Returns 400 if expired, 404 if invalid/used.
  - Throttling: authenticated 30/min

- POST /api/v1/devices/check-activation/
  - Body: { "device_id": "string" }
  - Returns activation status and expires_in_seconds if pending.
  - Throttling: anonymous 20/min, authenticated 60/min

- GET /api/v1/devices/current-campaign/?device_id=...
  - Returns campaign details and media items.
  - Now includes: normalize_to_orientation: "none" | "portrait" | "landscape"

## Notes
- Codes are 6 chars (A–Z, 0–9) and checked for uniqueness.
- Mobile app should refresh the code if expires_in_seconds <= 0.
- Web dashboard can show a countdown during activation.

## Frontend (Web) changes
- Added simple “Get Code” helper in Display Management to request a code for a given Device ID and show a countdown; auto-refreshes when expired.
- TV simulator now:
  - Requests activation code on start when not activated.
  - Shows an expiry countdown and auto-refreshes the code.
  - Honors normalize_to_orientation hint for image rotation.

## Quick Smoke Tests
1) Request activation code twice within 15 min for same device_id → same code; expires_in_seconds decreases.
2) Wait >15 min or set activation_code_created_at back in DB → request again → new code.
3) Try activating with an expired code → 400 with error message.
4) Call current-campaign and confirm normalize_to_orientation field present.

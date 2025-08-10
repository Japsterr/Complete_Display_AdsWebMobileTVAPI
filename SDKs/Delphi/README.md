# Delphi SDK for DisplayAds API

This folder contains the Delphi unit `DisplayAdsAPI.pas`, a lightweight wrapper around the DisplayAds REST API.

- Auth (login, refresh, logout)
- Media (list, upload via multipart)
- Campaigns (list, create, assign media)
- Displays & Activation (list, request activation code, activate)
- Analytics (summary, campaign breakdown, CSV exports)
- Telemetry (device heartbeat, media impression)

## Quick Start

1. Add `DisplayAdsAPI.pas` to your Delphi project.
2. Use it like:

```
var
  Client: TDisplayAdsClient;
  Ok: Boolean;
  MediaJson: TJSONValue;
begin
  Client := TDisplayAdsClient.Create('https://your-server.example.com');
  try
    Ok := Client.Login('user@example.com', 'password');
    if not Ok then raise Exception.Create('Login failed');

    MediaJson := Client.ListMedia; // Remember to free JSON values you own when done
    try
      // Inspect JSON
    finally
      MediaJson.Free;
    end;
  finally
    Client.Free;
  end;
end;
```

## Notes
- Base URL should include scheme and host (e.g., `https://...`).
- JSON results are returned as `TJSONValue`; cast to `TJSONObject`/`TJSONArray` as needed.
- For file uploads, ensure the file path exists and is readable.
- On HTTP 401, the client attempts a refresh on next call; handle exceptions accordingly.

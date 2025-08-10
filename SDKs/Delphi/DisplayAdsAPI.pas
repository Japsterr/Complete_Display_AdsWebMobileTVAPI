unit DisplayAdsAPI;

interface

uses
  System.SysUtils, System.Classes, System.JSON, System.Net.HttpClient, System.Net.HttpClientComponent,
  System.Net.URLClient, System.Generics.Collections;

type
  TAuthTokens = record
    AccessToken: string;
    RefreshToken: string;
  end;

  TDisplayAdsClient = class
  private
    FBaseUrl: string;
    FHttp: THTTPClient;
    FTokens: TAuthTokens;
    function BuildUrl(const Path: string): string;
    procedure SetAuthHeader;
    function HandleResponse(const Resp: IHTTPResponse): TJSONValue;
    function PostJson(const Path: string; const Body: TJSONObject; Auth: Boolean = True): TJSONValue;
    function GetJson(const Path: string; const Query: string = ''; Auth: Boolean = True): TJSONValue;
    function DeleteJson(const Path: string; Auth: Boolean = True): TJSONValue;
    function PatchJson(const Path: string; const Body: TJSONObject; Auth: Boolean = True): TJSONValue;
    function GetCsv(const Path, Query: string): string;
  public
    constructor Create(const ABaseUrl: string);
    destructor Destroy; override;

    // Auth
    function Login(const Email, Password: string): Boolean;
    procedure Logout;
    function RefreshAccessToken: Boolean;
    function IsAuthenticated: Boolean;

    // Profile
    function GetProfile: TJSONValue;

    // Media
    function ListMedia: TJSONValue;
    function UploadMedia(const FilePath, Name, MediaType: string; const Description: string = ''): TJSONValue;

    // Campaigns
    function ListCampaigns: TJSONValue;
    function CreateCampaign(const Name, Orientation, NormalizeHint: string; const Description: string = ''): TJSONValue;
    function AddMediaToCampaign(CampaignId, MediaId: Integer; DurationSeconds, OrderIndex: Integer): TJSONValue;
  // Campaign Assignment & Broadcast
  function AssignCampaignToDisplays(CampaignId: Integer; const DisplayIds: TArray<Integer>; const StartISO: string = ''; const EndISO: string = ''; Priority: Integer = 0): TJSONValue;
  function AssignCampaignToGroup(CampaignId, GroupId: Integer; const StartISO: string = ''; const EndISO: string = ''; Priority: Integer = 0): TJSONValue;
  function BroadcastCampaign(CampaignId: Integer; const StartISO: string = ''; const EndISO: string = ''; Priority: Integer = 0): TJSONValue;
  function QueueCampaignForDisplays(CampaignId: Integer; const DisplayIds: TArray<Integer>; DurationMinutes: Integer; Priority: Integer = 0): TJSONValue;

    // Displays & Activation
    function ListDisplays: TJSONValue;
    function RequestActivationCode(const DeviceId: string; const DeviceInfoJson: string = '{}'): TJSONValue;
    function ActivateDevice(const ActivationCode, DisplayName, Location: string): TJSONValue;
    function GetDeviceCampaign(const DeviceId: string): TJSONValue;

    // Analytics
    function AnalyticsSummary(const StartISO, EndISO, Granularity: string): TJSONValue;
    function AnalyticsCampaignBreakdown(const StartISO, EndISO: string): TJSONValue;
    function ExportImpressionsCSV(const StartISO, EndISO: string): string;
    function ExportDevicesCSV(const StartISO, EndISO: string): string;

    // Telemetry
    procedure DeviceHeartbeat(const DeviceId, Status, DeviceInfoJson: string);
    procedure RecordMediaImpression(const DeviceId: string; MediaId, CampaignId, DurationShown, ScheduledDuration, SequenceNumber, TotalMedia: Integer; Completed: Boolean);

    property Tokens: TAuthTokens read FTokens;
  end;

implementation

function TDisplayAdsClient.BuildUrl(const Path: string): string;
begin
  if Path.StartsWith('/') then Result := FBaseUrl + Path else Result := FBaseUrl + '/' + Path;
end;

procedure TDisplayAdsClient.SetAuthHeader;
begin
  if FTokens.AccessToken <> '' then FHttp.CustomHeaders['Authorization'] := 'Bearer ' + FTokens.AccessToken
  else FHttp.CustomHeaders['Authorization'] := '';
end;

function TDisplayAdsClient.HandleResponse(const Resp: IHTTPResponse): TJSONValue;
var Body: string;
begin
  if Resp = nil then raise Exception.Create('No response');
  Body := Resp.ContentAsString(TEncoding.UTF8);
  if (Resp.StatusCode >= 200) and (Resp.StatusCode < 300) then
  begin
    if Body.Trim = '' then Exit(nil);
    Result := TJSONObject.ParseJSONValue(Body);
  end
  else if Resp.StatusCode = 401 then
  begin
    if RefreshAccessToken then raise Exception.Create('Retry after refresh');
    raise Exception.CreateFmt('Unauthorized (%d): %s', [Resp.StatusCode, Body]);
  end
  else
    raise Exception.CreateFmt('HTTP %d: %s', [Resp.StatusCode, Body]);
end;

function TDisplayAdsClient.PostJson(const Path: string; const Body: TJSONObject; Auth: Boolean): TJSONValue;
var Resp: IHTTPResponse; S: TStringStream;
begin
  if Auth then SetAuthHeader;
  S := TStringStream.Create(Body.ToJSON, TEncoding.UTF8);
  try
    Resp := FHttp.Post(BuildUrl(Path), S);
    Result := HandleResponse(Resp);
  finally
    S.Free;
  end;
end;

function TDisplayAdsClient.PatchJson(const Path: string; const Body: TJSONObject; Auth: Boolean): TJSONValue;
var Req: IHTTPRequest; Resp: IHTTPResponse;
begin
  if Auth then SetAuthHeader;
  Req := FHttp.GetRequest('PATCH', BuildUrl(Path));
  Req.SetContent(Body.ToJSON, TEncoding.UTF8, 'application/json');
  Resp := FHttp.Execute(Req, nil);
  Result := HandleResponse(Resp);
end;

function TDisplayAdsClient.GetJson(const Path: string; const Query: string; Auth: Boolean): TJSONValue;
var Resp: IHTTPResponse; Url: string;
begin
  if Auth then SetAuthHeader;
  if Query <> '' then Url := BuildUrl(Path) + '?' + Query else Url := BuildUrl(Path);
  Resp := FHttp.Get(Url);
  Result := HandleResponse(Resp);
end;

function TDisplayAdsClient.DeleteJson(const Path: string; Auth: Boolean): TJSONValue;
var Resp: IHTTPResponse;
begin
  if Auth then SetAuthHeader;
  Resp := FHttp.Delete(BuildUrl(Path));
  Result := HandleResponse(Resp);
end;

function TDisplayAdsClient.GetCsv(const Path, Query: string): string;
var Resp: IHTTPResponse; Url: string;
begin
  SetAuthHeader;
  if Query <> '' then Url := BuildUrl(Path) + '?' + Query else Url := BuildUrl(Path);
  Resp := FHttp.Get(Url);
  if (Resp.StatusCode >= 200) and (Resp.StatusCode < 300) then
    Result := Resp.ContentAsString(TEncoding.UTF8)
  else
    raise Exception.CreateFmt('HTTP %d: %s', [Resp.StatusCode, Resp.ContentAsString(TEncoding.UTF8)]);
end;

constructor TDisplayAdsClient.Create(const ABaseUrl: string);
begin
  inherited Create;
  FBaseUrl := ABaseUrl.TrimRight(['/']);
  FHttp := THTTPClient.Create;
  FHttp.ContentType := 'application/json';
  FHttp.Accept := 'application/json';
  FTokens.AccessToken := '';
  FTokens.RefreshToken := '';
end;

destructor TDisplayAdsClient.Destroy;
begin
  FHttp.Free;
  inherited;
end;

function TDisplayAdsClient.Login(const Email, Password: string): Boolean;
var Body: TJSONObject; Resp: TJSONValue; Obj: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('email', Email);
    Body.AddPair('password', Password);
    Resp := PostJson('/api/v1/login/', Body, False);
    try
      if (Resp <> nil) and (Resp is TJSONObject) then
      begin
        Obj := TJSONObject(Resp);
        FTokens.AccessToken := Obj.GetValue<string>('access', '');
        FTokens.RefreshToken := Obj.GetValue<string>('refresh', '');
        Result := FTokens.AccessToken <> '';
      end
      else Result := False;
    finally
      Resp.Free;
    end;
  finally
    Body.Free;
  end;
end;

procedure TDisplayAdsClient.Logout;
var Body: TJSONObject; Resp: TJSONValue;
begin
  if FTokens.RefreshToken = '' then Exit;
  Body := TJSONObject.Create;
  try
    Body.AddPair('refresh', FTokens.RefreshToken);
    Resp := PostJson('/api/v1/logout/', Body, True);
    if Assigned(Resp) then Resp.Free;
  finally
    Body.Free;
  end;
  FTokens.AccessToken := '';
  FTokens.RefreshToken := '';
end;

function TDisplayAdsClient.RefreshAccessToken: Boolean;
var Body: TJSONObject; Resp: TJSONValue; Obj: TJSONObject;
begin
  Result := False;
  if FTokens.RefreshToken = '' then Exit;
  Body := TJSONObject.Create;
  try
    Body.AddPair('refresh', FTokens.RefreshToken);
    Resp := PostJson('/api/v1/token/refresh/', Body, False);
    try
      if (Resp <> nil) and (Resp is TJSONObject) then
      begin
        Obj := TJSONObject(Resp);
        FTokens.AccessToken := Obj.GetValue<string>('access', '');
        Result := FTokens.AccessToken <> '';
      end;
    finally
      Resp.Free;
    end;
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.IsAuthenticated: Boolean;
begin
  Result := FTokens.AccessToken <> '';
end;

function TDisplayAdsClient.GetProfile: TJSONValue;
begin
  Result := GetJson('/api/v1/auth/profile/');
end;

function TDisplayAdsClient.ListMedia: TJSONValue;
begin
  Result := GetJson('/api/v1/media/');
end;

function TDisplayAdsClient.UploadMedia(const FilePath, Name, MediaType: string; const Description: string): TJSONValue;
var MClient: TNetHTTPClient; Form: TMultipartFormData; Resp: IHTTPResponse; Url: string;
begin
  Url := BuildUrl('/api/v1/media/');
  MClient := TNetHTTPClient.Create(nil);
  try
    if FTokens.AccessToken <> '' then
      MClient.CustomHeaders['Authorization'] := 'Bearer ' + FTokens.AccessToken;
    Form := TMultipartFormData.Create;
    try
      Form.AddField('name', Name);
      Form.AddField('media_type', MediaType);
      if Description <> '' then Form.AddField('description', Description);
      Form.AddFile('file', FilePath);
      Resp := MClient.Post(Url, Form);
      Result := HandleResponse(Resp);
    finally
      Form.Free;
    end;
  finally
    MClient.Free;
  end;
end;

function TDisplayAdsClient.ListCampaigns: TJSONValue;
begin
  Result := GetJson('/api/v1/campaigns/');
end;

function TDisplayAdsClient.CreateCampaign(const Name, Orientation, NormalizeHint: string; const Description: string): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('name', Name);
    if Description <> '' then Body.AddPair('description', Description);
    Body.AddPair('screen_orientation', Orientation);
    Body.AddPair('normalize_to_orientation', NormalizeHint);
    Result := PostJson('/api/v1/campaigns/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.AddMediaToCampaign(CampaignId, MediaId: Integer; DurationSeconds, OrderIndex: Integer): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('campaign', TJSONNumber.Create(CampaignId));
    Body.AddPair('media', TJSONNumber.Create(MediaId));
    Body.AddPair('display_duration_seconds', TJSONNumber.Create(DurationSeconds));
    Body.AddPair('order', TJSONNumber.Create(OrderIndex));
    Result := PostJson('/api/v1/campaign-media/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.AssignCampaignToDisplays(CampaignId: Integer; const DisplayIds: TArray<Integer>; const StartISO, EndISO: string; Priority: Integer): TJSONValue;
var Body: TJSONObject; Arr: TJSONArray; I: Integer;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('campaign_id', TJSONNumber.Create(CampaignId));
    Arr := TJSONArray.Create;
    for I := 0 to High(DisplayIds) do Arr.Add(DisplayIds[I]);
    Body.AddPair('display_ids', Arr);
    if (StartISO <> '') and (EndISO <> '') then
    begin
      Body.AddPair('start_datetime', StartISO);
      Body.AddPair('end_datetime', EndISO);
      Body.AddPair('priority', TJSONNumber.Create(Priority));
    end;
    Result := PostJson('/api/v1/campaigns/assign/displays/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.AssignCampaignToGroup(CampaignId, GroupId: Integer; const StartISO, EndISO: string; Priority: Integer): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('campaign_id', TJSONNumber.Create(CampaignId));
    Body.AddPair('group_id', TJSONNumber.Create(GroupId));
    if (StartISO <> '') and (EndISO <> '') then
    begin
      Body.AddPair('start_datetime', StartISO);
      Body.AddPair('end_datetime', EndISO);
      Body.AddPair('priority', TJSONNumber.Create(Priority));
    end;
    Result := PostJson('/api/v1/campaigns/assign/group/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.BroadcastCampaign(CampaignId: Integer; const StartISO, EndISO: string; Priority: Integer): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('campaign_id', TJSONNumber.Create(CampaignId));
    if (StartISO <> '') and (EndISO <> '') then
    begin
      Body.AddPair('start_datetime', StartISO);
      Body.AddPair('end_datetime', EndISO);
      Body.AddPair('priority', TJSONNumber.Create(Priority));
    end;
    Result := PostJson('/api/v1/campaigns/broadcast/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.QueueCampaignForDisplays(CampaignId: Integer; const DisplayIds: TArray<Integer>; DurationMinutes: Integer; Priority: Integer): TJSONValue;
var Body: TJSONObject; Arr: TJSONArray; I: Integer;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('campaign_id', TJSONNumber.Create(CampaignId));
    Arr := TJSONArray.Create;
    for I := 0 to High(DisplayIds) do Arr.Add(DisplayIds[I]);
    Body.AddPair('display_ids', Arr);
    Body.AddPair('duration_minutes', TJSONNumber.Create(DurationMinutes));
    Body.AddPair('priority', TJSONNumber.Create(Priority));
    Result := PostJson('/api/v1/campaigns/queue/displays/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.ListDisplays: TJSONValue;
begin
  Result := GetJson('/api/v1/displays/');
end;

function TDisplayAdsClient.RequestActivationCode(const DeviceId: string; const DeviceInfoJson: string): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('device_id', DeviceId);
    if DeviceInfoJson <> '' then
      Body.AddPair('device_info', TJSONObject.ParseJSONValue(DeviceInfoJson) as TJSONValue)
    else
      Body.AddPair('device_info', TJSONObject.Create);
    Result := PostJson('/api/v1/devices/request-activation/', Body, False);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.ActivateDevice(const ActivationCode, DisplayName, Location: string): TJSONValue;
var Body: TJSONObject;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('activation_code', ActivationCode);
    if DisplayName <> '' then Body.AddPair('display_name', DisplayName);
    if Location <> '' then Body.AddPair('location', Location);
    Result := PostJson('/api/v1/devices/activate/', Body, True);
  finally
    Body.Free;
  end;
end;

function TDisplayAdsClient.GetDeviceCampaign(const DeviceId: string): TJSONValue;
begin
  Result := GetJson('/api/v1/devices/current-campaign/', 'device_id=' + TNetEncoding.URL.Encode(DeviceId), False);
end;

function TDisplayAdsClient.AnalyticsSummary(const StartISO, EndISO, Granularity: string): TJSONValue;
var Q: string;
begin
  Q := '';
  if StartISO <> '' then Q := Q + 'start=' + TNetEncoding.URL.Encode(StartISO);
  if EndISO <> '' then
  begin
    if Q <> '' then Q := Q + '&';
    Q := Q + 'end=' + TNetEncoding.URL.Encode(EndISO);
  end;
  if Granularity <> '' then
  begin
    if Q <> '' then Q := Q + '&';
    Q := Q + 'granularity=' + TNetEncoding.URL.Encode(Granularity);
  end;
  Result := GetJson('/api/v1/analytics/summary/', Q, True);
end;

function TDisplayAdsClient.AnalyticsCampaignBreakdown(const StartISO, EndISO: string): TJSONValue;
var Q: string;
begin
  Q := '';
  if StartISO <> '' then Q := Q + 'start=' + TNetEncoding.URL.Encode(StartISO);
  if EndISO <> '' then
  begin
    if Q <> '' then Q := Q + '&';
    Q := Q + 'end=' + TNetEncoding.URL.Encode(EndISO);
  end;
  Result := GetJson('/api/v1/analytics/campaign-breakdown/', Q, True);
end;

function TDisplayAdsClient.ExportImpressionsCSV(const StartISO, EndISO: string): string;
var Q: string;
begin
  Q := '';
  if StartISO <> '' then Q := Q + 'start=' + TNetEncoding.URL.Encode(StartISO);
  if EndISO <> '' then
  begin
    if Q <> '' then Q := Q + '&';
    Q := Q + 'end=' + TNetEncoding.URL.Encode(EndISO);
  end;
  Result := GetCsv('/api/v1/analytics/export/impressions.csv', Q);
end;

function TDisplayAdsClient.ExportDevicesCSV(const StartISO, EndISO: string): string;
var Q: string;
begin
  Q := '';
  if StartISO <> '' then Q := Q + 'start=' + TNetEncoding.URL.Encode(StartISO);
  if EndISO <> '' then
  begin
    if Q <> '' then Q := Q + '&';
    Q := Q + 'end=' + TNetEncoding.URL.Encode(EndISO);
  end;
  Result := GetCsv('/api/v1/analytics/export/devices.csv', Q);
end;

procedure TDisplayAdsClient.DeviceHeartbeat(const DeviceId, Status, DeviceInfoJson: string);
var Body: TJSONObject; Resp: TJSONValue;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('device_id', DeviceId);
    if Status <> '' then Body.AddPair('status', Status) else Body.AddPair('status', 'online');
    if DeviceInfoJson <> '' then
      Body.AddPair('device_info', TJSONObject.ParseJSONValue(DeviceInfoJson) as TJSONValue)
    else
      Body.AddPair('device_info', TJSONObject.Create);
    Resp := PostJson('/api/v1/analytics/heartbeat/', Body, False);
    if Assigned(Resp) then Resp.Free;
  finally
    Body.Free;
  end;
end;

procedure TDisplayAdsClient.RecordMediaImpression(const DeviceId: string; MediaId, CampaignId, DurationShown, ScheduledDuration, SequenceNumber, TotalMedia: Integer; Completed: Boolean);
var Body: TJSONObject; Resp: TJSONValue;
begin
  Body := TJSONObject.Create;
  try
    Body.AddPair('device_id', DeviceId);
    Body.AddPair('media_id', TJSONNumber.Create(MediaId));
    Body.AddPair('campaign_id', TJSONNumber.Create(CampaignId));
    Body.AddPair('duration_shown', TJSONNumber.Create(DurationShown));
    Body.AddPair('scheduled_duration', TJSONNumber.Create(ScheduledDuration));
    Body.AddPair('completed', TJSONBool.Create(Completed));
    Body.AddPair('sequence_number', TJSONNumber.Create(SequenceNumber));
    Body.AddPair('total_media_in_campaign', TJSONNumber.Create(TotalMedia));
    Resp := PostJson('/api/v1/analytics/impression/', Body, False);
    if Assigned(Resp) then Resp.Free;
  finally
    Body.Free;
  end;
end;

end.

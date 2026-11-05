param(
    [string]$RuntimeRoot = (Join-Path $env:LOCALAPPDATA "LabQuorum"),
    [string]$ConsolePath,
    [string]$CdpUrl = "http://127.0.0.1:9333"
)

$ErrorActionPreference = "Stop"

$runtime = [System.IO.Path]::GetFullPath($RuntimeRoot)
$codexHome = Join-Path $runtime "codex-home"
$codexConfig = Join-Path $codexHome "config.toml"
if (-not (Test-Path -LiteralPath $codexConfig -PathType Leaf)) {
    throw "Run lq setup first. Missing runtime Codex config: $codexConfig"
}

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathParts = @($machinePath, $userPath) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
$env:Path = $pathParts -join ";"
$env:CODEX_HOME = $codexHome

$whoami = Get-Command "whoami.exe" -ErrorAction Stop
$sidOutput = & $whoami.Source /user /fo csv /nh
$sidMatch = [regex]::Match(($sidOutput -join "`n"), "S-1-\d+(?:-\d+)+")
if (-not $sidMatch.Success) {
    throw "Could not determine the current Windows SID for the agent write policy."
}
$icacls = Get-Command "icacls.exe" -ErrorAction Stop
foreach ($agentName in @("labops", "pi-desk")) {
    $agentDirectory = Join-Path $runtime (Join-Path "agents" $agentName)
    if (-not (Test-Path -LiteralPath $agentDirectory -PathType Container)) {
        throw "Missing LabQuorum agent directory: $agentDirectory"
    }
    $denyEntry = "*$($sidMatch.Value):(OI)(CI)(W)"
    $null = & $icacls.Source $agentDirectory /deny $denyEntry /T /C /Q
    if ($LASTEXITCODE -ne 0) {
        throw "Could not apply the read-only agent directory policy to $agentDirectory"
    }
    $probePath = Join-Path $agentDirectory ".lq-write-probe-$([guid]::NewGuid().ToString('N'))"
    $writeDenied = $false
    try {
        [System.IO.File]::WriteAllText($probePath, "probe", [System.Text.Encoding]::UTF8)
    }
    catch [System.UnauthorizedAccessException] {
        $writeDenied = $true
    }
    catch [System.IO.IOException] {
        $writeDenied = $_.Exception.HResult -eq -2147024891
    }
    finally {
        if (Test-Path -LiteralPath $probePath) {
            Remove-Item -LiteralPath $probePath -Force
        }
    }
    if (-not $writeDenied) {
        throw "The current user can still write to the LabQuorum agent directory: $agentDirectory"
    }
}

$existing = @(Get-Process -Name "Switch Console" -ErrorAction SilentlyContinue)
if ($existing.Count -gt 0) {
    $windows = @($existing | Where-Object { $_.MainWindowHandle -ne 0 })
    if ($windows.Count -eq 0) {
        throw "Switch Console is running without a closable main window. Close it gracefully and retry."
    }
    foreach ($process in $windows) {
        if (-not $ConsolePath -and $process.Path) {
            $ConsolePath = $process.Path
        }
        if (-not $process.CloseMainWindow()) {
            throw "Switch Console process $($process.Id) did not accept a graceful close request."
        }
    }
    foreach ($process in $windows) {
        if (-not $process.WaitForExit(30000)) {
            throw "Switch Console process $($process.Id) did not close within 30 seconds."
        }
    }
}

if (-not $ConsolePath) {
    $ConsolePath = Join-Path $env:LOCALAPPDATA "Programs\Switch Console\Switch Console.exe"
}
$console = [System.IO.Path]::GetFullPath($ConsolePath)
if (-not (Test-Path -LiteralPath $console -PathType Leaf)) {
    throw "Could not find Switch Console.exe at $console. Pass -ConsolePath explicitly."
}

$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $console
$startInfo.WorkingDirectory = Split-Path -LiteralPath $console -Parent
$startInfo.UseShellExecute = $false
$startInfo.ArgumentList.Add("--remote-debugging-port=9333")
$started = [System.Diagnostics.Process]::Start($startInfo)
if ($null -eq $started) {
    throw "Could not start Switch Console."
}

$client = [System.Net.Http.HttpClient]::new()
$deadline = [DateTimeOffset]::UtcNow.AddSeconds(90)
try {
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        try {
            $response = $client.GetAsync("$($CdpUrl.TrimEnd('/'))/json/version").GetAwaiter().GetResult()
            if ($response.IsSuccessStatusCode) {
                $version = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult() | ConvertFrom-Json
                Write-Output "Switch Console CDP is ready: $($version.Browser)"
                Write-Output "CODEX_HOME=$env:CODEX_HOME"
                return
            }
        }
        catch [System.Net.Http.HttpRequestException] {
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    $client.Dispose()
}
throw "Switch Console did not expose CDP at $CdpUrl/json/version within 90 seconds."

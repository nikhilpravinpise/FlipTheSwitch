[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ConsoleExecutable,

    [Parameter(Mandatory = $true)]
    [string] $RuntimeRoot,

    [switch] $CloseExisting
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Machine = [System.Environment]::MachineName
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$resolvedExecutable = (Resolve-Path -LiteralPath $ConsoleExecutable).Path
$resolvedRoot = [System.IO.Path]::GetFullPath($RuntimeRoot)
$codexHome = Join-Path $resolvedRoot "codex-home"
$configPath = Join-Path $codexHome "config.toml"

if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Runtime Codex config is missing: $configPath"
}

$currentProcesses = Get-CimInstance -ClassName Win32_Process -ComputerName $Machine |
    Where-Object { $_.Name -in @("Switch.exe", "switch.exe") }
foreach ($currentProcess in $currentProcesses) {
    $owner = Invoke-CimMethod -InputObject $currentProcess -MethodName GetOwner
    if ($owner.ReturnValue -eq 0 -and "$($owner.Domain)\$($owner.User)" -eq $User) {
        if (-not $CloseExisting) {
            throw "Switch Console is already running for $User on $Machine. Close it or pass -CloseExisting."
        }
        $process = Get-Process -Id $currentProcess.ProcessId -ErrorAction SilentlyContinue
        if ($null -ne $process -and -not $process.CloseMainWindow()) {
            throw "Could not request a graceful close for Switch Console process $($process.Id)."
        }
        if ($null -ne $process) {
            Wait-Process -Id $process.Id -Timeout 15
        }
    }
}

$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $resolvedExecutable
$startInfo.WorkingDirectory = $resolvedRoot
$startInfo.UseShellExecute = $false
$startInfo.ArgumentList.Add("--remote-debugging-port=9333")
$startInfo.Environment["CODEX_HOME"] = $codexHome
$consoleProcess = [System.Diagnostics.Process]::Start($startInfo)
if ($null -eq $consoleProcess) {
    throw "Switch Console did not start."
}

$deadline = [DateTimeOffset]::UtcNow.AddSeconds(30)
while ([DateTimeOffset]::UtcNow -lt $deadline) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:9333/json/version" -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Output ([pscustomobject]@{
                Machine = $Machine
                User = $User
                ProcessId = $consoleProcess.Id
                CodexHome = $codexHome
                DebugEndpoint = "http://127.0.0.1:9333/json/version"
            } | ConvertTo-Json -Compress)
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

throw "Switch Console did not expose its local debugging endpoint before the timeout."

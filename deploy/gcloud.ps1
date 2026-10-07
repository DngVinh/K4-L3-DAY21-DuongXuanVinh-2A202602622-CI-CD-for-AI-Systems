<#
Run the workspace-local Google Cloud CLI with isolated configuration.
Examples:
  .\deploy\gcloud.ps1 version
  .\deploy\gcloud.ps1 auth login --update-adc
  .\deploy\gcloud.ps1 projects describe lday21-income-mlops
#>
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $GcloudArguments
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent (Resolve-Path -LiteralPath $PSScriptRoot).Path
$sdkPath = Join-Path $workspaceRoot '.tools\google-cloud-sdk\bin\gcloud.cmd'
$pythonPath = Join-Path $workspaceRoot '.venv\Scripts\python.exe'
$configPath = [System.IO.Path]::GetFullPath(
    (Join-Path $workspaceRoot '.tools\gcloud-config')
)
if (-not $configPath.StartsWith(
    $workspaceRoot + [System.IO.Path]::DirectorySeparatorChar,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw 'Cloud SDK configuration must stay inside the workspace.'
}
if (-not (Test-Path -LiteralPath $sdkPath) -or
    -not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Workspace Google Cloud CLI or Python environment is missing.'
}
if ((Test-Path -LiteralPath $configPath) -and
    ((Get-Item -LiteralPath $configPath).Attributes -band
        [System.IO.FileAttributes]::ReparsePoint)) {
    throw 'Cloud SDK configuration cannot be a symlink or junction.'
}

$previousConfig = $env:CLOUDSDK_CONFIG
$previousPython = $env:CLOUDSDK_PYTHON
$previousProject = $env:CLOUDSDK_CORE_PROJECT
try {
    $env:CLOUDSDK_CONFIG = $configPath
    $env:CLOUDSDK_PYTHON = $pythonPath
    $env:CLOUDSDK_CORE_PROJECT = 'lday21-income-mlops'
    & $sdkPath @GcloudArguments
    $sdkExitCode = $LASTEXITCODE
}
finally {
    $env:CLOUDSDK_CONFIG = $previousConfig
    $env:CLOUDSDK_PYTHON = $previousPython
    $env:CLOUDSDK_CORE_PROJECT = $previousProject
}
exit $sdkExitCode

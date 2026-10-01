$ErrorActionPreference = 'Stop'
Add-Type -Path '/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity/Plugins/dnlib.dll'
$assemblyPath = '/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/Managed/UnityEngine/UnityEditor.CoreModule.dll'
$module = [dnlib.DotNet.ModuleDefMD]::Load($assemblyPath)
try {
    $type = $module.GetTypes() | Where-Object FullName -eq 'UnityEditor.Build.Reporting.BuildSummary'
    if ($null -eq $type) { throw 'BuildSummary type missing' }
    $rows = @($type.Methods | Where-Object { $_.Name.String -in @('get_totalErrors','get_totalWarnings') } | ForEach-Object { [ordered]@{ name=$_.Name.String; returnType=$_.MethodSig.RetType.FullName; signature=$_.FullName } })
    if ($rows.Count -ne 2) { throw 'Expected two count getters' }
    [ordered]@{kind='ReadOnlyPinnedUnityApiMetadata'; utc=[DateTime]::UtcNow.ToString('o'); path=$assemblyPath; sha256=(Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256).Hash.ToLowerInvariant(); assembly=$module.Assembly.FullName; type=$type.FullName; methods=$rows; scope='Metadata only; no Unity launch, compilation, code change or assembly execution'} | ConvertTo-Json -Depth 8
} finally { $module.Dispose() }

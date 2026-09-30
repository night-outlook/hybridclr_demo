$ErrorActionPreference = 'Stop'
Add-Type -Path '/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity/Plugins/dnlib.dll'
$fixtureRoot = '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime/host/player-fixtures'
$rows = @(Get-ChildItem -LiteralPath $fixtureRoot -Filter '*.dll' -Recurse | Sort-Object FullName | ForEach-Object {
    $module = [dnlib.DotNet.ModuleDefMD]::Load($_.FullName)
    try {
        [ordered]@{ path=$_.FullName; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant(); assembly=$module.Assembly.FullName; assemblyFlags=[int]$module.Assembly.Attributes; hasPublicKey=$module.Assembly.HasPublicKey; publicKeyHex=[Convert]::ToHexString($module.Assembly.PublicKey.Data); references=@($module.GetAssemblyRefs() | ForEach-Object { [ordered]@{name=$_.FullName; flags=[int]$_.Attributes; hasPublicKey=$_.HasPublicKey; keyOrTokenHex=[Convert]::ToHexString($_.PublicKeyOrToken.Data)} }) }
    } finally { $module.Dispose() }
})
[ordered]@{kind='ReadOnlyFixtureMetadataInspection'; startedScope='Metadata only; no fixture execution, compilation or rewrite'; files=$rows} | ConvertTo-Json -Depth 10

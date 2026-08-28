$ErrorActionPreference = "Stop"
Add-Type -Path "/Users/ah/GitHub/hybridclr/hybridclr_unity/Plugins/dnlib.dll"
$dllPath = "/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/_temp/AssemblyShadow/M04PlayerInputs-b7510196acb241f2ab40a72906a34c7c/LinkedPlayer/Assemblies/mscorlib.dll"
$receiptPath = "/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/_temp/AssemblyShadow/M04PlayerInputs-b7510196acb241f2ab40a72906a34c7c/m04-player-build.json"
$dllHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dllPath).Hash.ToLowerInvariant()
$receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
$bound = @($receipt.assemblyIdentities | Where-Object name -eq "mscorlib")
if ($bound.Count -ne 1 -or $bound[0].path -ne $dllPath -or $bound[0].sha256 -ne $dllHash) { throw "Linked mscorlib receipt mismatch" }
$module = [dnlib.DotNet.ModuleDefMD]::Load($dllPath)
try {
  if ($module.Mvid.ToString() -ne $bound[0].mvid) { throw "Linked MVID mismatch" }
  $methods = @(
    foreach ($typeName in "System.Reflection.Assembly", "System.AppDomain") {
      $type = $module.Types | Where-Object FullName -eq $typeName | Select-Object -First 1
      foreach ($method in $type.Methods | Where-Object { $_.Name -match "^(Load|LoadAssembly|LoadAssemblyRaw|LoadFrom|GetAssemblies)$" }) {
        [ordered]@{
          signature = $method.FullName
          metadataToken = $method.MDToken.Raw
          implementation = $method.ImplAttributes.ToString()
          hasBody = $method.HasBody
          instructions = @(
            if ($method.HasBody) {
              foreach ($instruction in $method.Body.Instructions) {
                [ordered]@{ offset = $instruction.Offset; opcode = $instruction.OpCode.Name; operand = [string]$instruction.Operand }
              }
            }
          )
          exceptionHandlers = @(
            if ($method.HasBody) {
              foreach ($handler in $method.Body.ExceptionHandlers) {
                [ordered]@{ handlerType = $handler.HandlerType.ToString(); catchType = [string]$handler.CatchType; tryStart = [string]$handler.TryStart; tryEnd = [string]$handler.TryEnd; handlerStart = [string]$handler.HandlerStart; handlerEnd = [string]$handler.HandlerEnd; filterStart = [string]$handler.FilterStart }
              }
            }
          )
        }
      }
    }
  )
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath $dllPath).Hash.ToLowerInvariant() -ne $dllHash) { throw "Linked DLL changed during capture" }
  [ordered]@{
    schemaVersion = 1
    kind = "M04LinkedManagedLoadWrapperIL"
    assemblyPath = $dllPath
    assemblySha256 = $dllHash
    assemblyFullName = $module.Assembly.FullName
    assemblyMvid = $module.Mvid.ToString()
    playerBuildReceiptPath = $receiptPath
    playerBuildReceiptSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $receiptPath).Hash.ToLowerInvariant()
    buildGuid = $receipt.buildGuid
    nativeLibrarySha256 = $receipt.nativeLibrarySha256
    methods = $methods
  } | ConvertTo-Json -Depth 12
} finally { $module.Dispose() }

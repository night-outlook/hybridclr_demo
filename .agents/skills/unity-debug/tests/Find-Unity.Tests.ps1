$scriptPath = Join-Path $PSScriptRoot "../scripts/Find-Unity.ps1"

Describe "Find-Unity" {
    It "discovers the official Unity Hub executable on macOS" {
        $source = Get-Content -Raw $scriptPath
        $source | Should -Match '/Applications/Unity/Hub/Editor/\$Version/Unity\.app/Contents/MacOS/Unity'
        $source | Should -Match '\[System\.IO\.Path\]::PathSeparator'
    }

    It "retains Windows Hub discovery" {
        (Get-Content -Raw $scriptPath) | Should -Match 'Editor\\Unity\.exe'
    }
}

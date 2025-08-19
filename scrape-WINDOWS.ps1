<#
.SYNOPSIS
    Convenience launcher for the MYGA scraper on Windows PowerShell.

.DESCRIPTION
    Automatically activates the local Python virtual-environment (if present)
    and runs either scrape_and_save.py (default) or scrape_and_load.py.

.PARAMETER Action
    'save' : scrape and write JSON/CSV files only (default)
    'load' : scrape, write JSON/CSV, and load to the database

.EXAMPLE
    PS> ./run_scraper.ps1            # default 'save'
    PS> ./run_scraper.ps1 load       # run full scrape and load
#>
param(
    [ValidateSet('save','load')]
    [string]$Action = 'save'
)

# 1. Switch to script directory (project root)
Set-Location -Path $PSScriptRoot

# 2. Activate virtual-environment if it exists
$activatePath = Join-Path $PSScriptRoot '.venv\Scripts\Activate.ps1'
if (Test-Path $activatePath) {
    & $activatePath | Out-Null
}

# 3. Pick the target Python script
$pyScript = if ($Action -eq 'load') { 'scraping\scrape_and_load.py' } else { 'scraping\scrape_and_save.py' }

# 4. Execute with python (python.exe resolves inside venv if activated)
python $pyScript

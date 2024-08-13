param (
    [string]$sourcePath
)

# Define destination directories
$grasshopperLibDir = "$env:APPDATA\Grasshopper\Libraries"
$grasshopperUserObjectsDir = "$env:APPDATA\Grasshopper\UserObjects"
$rhinoPluginsDir = "$env:APPDATA\McNeel\Rhinoceros\7.0\Plug-ins"
$topLevelDir = "$env:APPDATA\Rhino-Plugin-Backup"
$miscDir = "$env:APPDATA\Rhino-Plugin-Backup\Misc"

# Ensure the Misc directory exists
if (-not (Test-Path $miscDir)) {
    New-Item -ItemType Directory -Path $miscDir -Force
}

# Function to copy directories
function Copy-Directory {
    param (
        [string]$source,
        [string]$destination
    )

    if (-not (Test-Path $destination)) {
        New-Item -ItemType Directory -Path $destination -Force
    }

    Copy-Item -Path $source\* -Destination $destination -Recurse -Force
}

# Function to copy files to top-level locations
function Copy-FilesToTopLevel {
    param (
        [string]$file,
        [string]$destination
    )

    Copy-Item -Path $file -Destination $destination -Force
    Unblock-File -Path (Join-Path -Path $destination -ChildPath (Split-Path $file -Leaf))
}

# Function to handle single files
function Handle-SingleFile {
    param (
        [string]$file
    )

    if ((Get-Item $file).PSIsContainer) {
        Write-Host "Skipping directory: $file"
        return
    }

    $extension = [System.IO.Path]::GetExtension($file)
    if (-not $extension) {
        Write-Host "File without extension: $file"
        Copy-FilesToTopLevel -file $file -destination $miscDir
        return
    }

    switch ($extension) {
        ".gha" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".ghpy" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".userobject" { Copy-FilesToTopLevel -file $file -destination $grasshopperUserObjectsDir }
        ".dll" { Copy-FilesToTopLevel -file $file -destination $rhinoPluginsDir }
        ".pisa" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".gh" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".3dm" { Copy-FilesToTopLevel -file $file -destination $rhinoPluginsDir }
        ".json" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".html" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".js" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".png" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".jpg" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".md" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".rb" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".xml" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".csv" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".osm" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".txt" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".pdf" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".exe" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".m" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".des" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".ptx" { Copy-FilesToTopLevel -file $file -destination $grasshopperLibDir }
        ".ghuser" { Copy-FilesToTopLevel -file $file -destination $grasshopperUserObjectsDir }
        default { Write-Host "Unsupported file type: $extension - File: $file" }
    }
}

# Check if the sourcePath is a directory or a file
if (Test-Path $sourcePath) {
    $destinationDir = "$topLevelDir\$(Split-Path -Path $sourcePath -Leaf)"
    Copy-Directory -source $sourcePath -destination $destinationDir

    Get-ChildItem -Path $sourcePath -Recurse | ForEach-Object {
        if (-not $_.PSIsContainer) {
            Handle-SingleFile -file $_.FullName
        }
    }

    Write-Host "All files and directories have been copied and unblocked successfully."
} else {
    Write-Host "The specified path does not exist."
}

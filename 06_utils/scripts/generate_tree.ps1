# Generate file tree excluding certain directories
Get-ChildItem -Path . -Recurse -Force |
  Where-Object { 
    $_.FullName -notmatch '\\\.git\\' -and
    $_.FullName -notmatch '\\node_modules\\' -and
    $_.FullName -notmatch '\\__pycache__\\' -and
    $_.FullName -notmatch '\\venv\\' -and
    $_.FullName -notmatch '\\\.[^\\]+\\' # Skip hidden folders
  } |
  ForEach-Object {
    $relativePath = $_.FullName.Replace($PWD.Path, '').TrimStart('\')
    if ($_.PSIsContainer) {
      "[DIR]  $relativePath"
    } else {
      "       $relativePath"
    }
  } | Out-File tree.txt -Encoding utf8

Write-Host "File tree generated in tree.txt"
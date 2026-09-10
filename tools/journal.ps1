<#
    Журнал ONE OF — локальный запуск.

    Держит на этом компьютере маленький веб-сервер, который раздаёт
    приложение из папки проекта по адресу http://localhost:8123/journal/.
    Порт менять нельзя: записи журнала браузер хранит отдельно для
    каждого адреса, и на другом порту они окажутся пустыми.

    Сервер слушает только сам компьютер (127.0.0.1), наружу и в
    локальную сеть ничего не отдаёт.

    Использование:
      journal.ps1            запустить сервер, если он ещё не запущен
      journal.ps1 -Open      то же плюс открыть журнал в браузере
      journal.ps1 -Install   создать ярлык на рабочем столе и автозапуск
      journal.ps1 -Uninstall убрать ярлык и автозапуск
      journal.ps1 -Stop      остановить сервер
#>

[CmdletBinding()]
param(
    [switch]$Open,
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Stop
)

$ErrorActionPreference = 'Stop'

$Port      = 8123
$Root      = Split-Path $PSScriptRoot -Parent
$Url       = "http://localhost:$Port/journal/"
$IconPath  = Join-Path $Root 'brand_assets\web\journal-icon.ico'
$Desktop   = [Environment]::GetFolderPath('Desktop')
$StartupNm = [Environment]::GetFolderPath('Startup')
$LinkName  = 'Журнал ONE OF.lnk'
$MarkerArg = 'one-of-journal-server'

function Test-ServerUp {
    $c = $null
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $task = $c.ConnectAsync('127.0.0.1', $Port)
        $finished = $task.Wait(400)
        # Wait() говорит лишь «задача завершилась» — успех проверяем отдельно
        return ($finished -and -not $task.IsFaulted -and $c.Connected)
    } catch {
        return $false
    } finally {
        if ($c) { $c.Close() }
    }
}

function Get-PythonW {
    $cmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        $exe = & python -c "import sys; print(sys.executable)"
        $w = $exe -replace 'python\.exe$', 'pythonw.exe'
        if (Test-Path $w) { return $w }
        return $exe
    }
    throw "Python не найден. Установите его с python.org или из Microsoft Store."
}

function Start-Server {
    if (Test-ServerUp) { return $false }
    if (-not (Test-Path (Join-Path $Root 'journal\index.html'))) {
        throw "Не вижу journal\index.html в папке $Root — похоже, проект переехал."
    }
    $pyw = Get-PythonW
    $srv = Join-Path $PSScriptRoot 'journal_server.py'
    if (-not (Test-Path $srv)) { throw "Не найден $srv" }
    # Аргументы — одной строкой: в пути проекта есть пробелы, а массив
    # -ArgumentList склеивает элементы через пробел и путь разваливается.
    $argLine = '"{0}" "{1}"' -f $srv, $Root
    Start-Process -FilePath $pyw -ArgumentList $argLine `
        -WorkingDirectory $Root -WindowStyle Hidden
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 150
        if (Test-ServerUp) { return $true }
    }
    throw "Сервер не поднялся за 6 секунд. Запустите journal.ps1 из PowerShell, чтобы увидеть ошибку."
}

function Stop-Server {
    $found = 0
    Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
        Where-Object { $_.CommandLine -and $_.CommandLine -match 'journal_server\.py' } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force
            $found++
        }
    return $found
}

function New-Shortcut($Path, $TargetVbs, $Description) {
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut($Path)
    $sc.TargetPath       = "$env:WINDIR\System32\wscript.exe"
    $sc.Arguments        = "`"$TargetVbs`""
    $sc.WorkingDirectory = $Root
    $sc.Description      = $Description
    if (Test-Path $IconPath) { $sc.IconLocation = "$IconPath,0" }
    $sc.Save()
}

if ($Stop) {
    $n = Stop-Server
    if ($n -gt 0) { "Сервер остановлен." } else { "Сервер и так не работал." }
    return
}

if ($Uninstall) {
    foreach ($p in @((Join-Path $Desktop $LinkName), (Join-Path $StartupNm $LinkName))) {
        if (Test-Path $p) { Remove-Item $p -Force; "Убрано: $p" }
    }
    "Ярлык и автозапуск удалены. Сам журнал и записи не тронуты."
    return
}

if ($Install) {
    $openVbs  = Join-Path $PSScriptRoot 'journal-open.vbs'
    $startVbs = Join-Path $PSScriptRoot 'journal-start.vbs'
    foreach ($f in @($openVbs, $startVbs)) {
        if (-not (Test-Path $f)) { throw "Не найден $f — файл должен лежать рядом с journal.ps1." }
    }

    New-Shortcut (Join-Path $Desktop $LinkName) $openVbs 'Журнал студии ONE OF — посещения и оплаты'
    "Ярлык на рабочем столе создан."

    New-Shortcut (Join-Path $StartupNm $LinkName) $startVbs 'Запуск журнала ONE OF при входе в Windows'
    "Автозапуск при входе в Windows настроен."

    if (Start-Server) { "Сервер запущен." } else { "Сервер уже работал." }
    ""
    "Готово. Журнал открывается ярлыком с рабочего стола, адрес: $Url"
    return
}

$started = Start-Server
if ($Open) {
    Start-Process $Url
} elseif ($started) {
    "Сервер запущен: $Url"
} else {
    "Сервер уже работает: $Url"
}

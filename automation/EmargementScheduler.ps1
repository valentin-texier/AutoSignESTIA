# Parametres
$calendarPath = "C:\WORKSPACE\Python\AutoEmargementPegasus\automation\calendar.ics"
$scriptPath = "C:\WORKSPACE\Python\AutoEmargementPegasus\run_AutoEmargementPegasus.py"
$logFilePath = "C:\WORKSPACE\Python\AutoEmargementPegasus\automation\log.txt"

# Demarrage de l'enregistrement du journal
Start-Transcript -Path $logFilePath

# Obtenir la date actuelle et ajouter 1 jour pour commencer l'analyse
$today = Get-Date
$tomorrow = $today.AddDays(1)
$endOfWeekNext = $tomorrow.AddDays(6) # Analyse jusqu'a 6 jours apres demain

# Verifier si le fichier ICS existe
if (-Not (Test-Path -Path $calendarPath)) {
    Write-Host "Le fichier $calendarPath est introuvable." -ForegroundColor Red
    Stop-Transcript
    exit 1
}

# Lire le fichier ICS
try {
    $calendarContent = Get-Content -Path $calendarPath
} catch {
    Write-Host "Erreur lors de la lecture du fichier calendrier : $_" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

# Initialiser un tableau pour stocker les heures de cours
$courseTimes = @()

# Analyser le fichier ICS pour trouver les evenements de la semaine a venir
foreach ($line in $calendarContent) {
    if ($line -match "^DTSTART;[^:]+:([0-9]{8}T[0-9]{6})$") {
        $eventDateTime = [datetime]::ParseExact($matches[1], "yyyyMMddTHHmmss", $null)
        if ($eventDateTime.Date -ge $tomorrow.Date -and $eventDateTime.Date -le $endOfWeekNext.Date) {
            $courseTimes += $eventDateTime
        }
    }
}

# Verifier si des cours ont ete trouves
if ($courseTimes.Count -eq 0) {
    Write-Host "Aucun cours trouve pour la semaine prochaine." -ForegroundColor Yellow
    Stop-Transcript
    exit 0
}

# Creer des taches planifiees pour chaque cours
foreach ($time in $courseTimes) {
    $emargementTime = $time.AddMinutes(10)

    # Verifier si la tache d'emargement existe deja
    $taskName = "Emargement_$($time.ToString('yyyyMMdd_HHmm'))"
    if (-not (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue)) {
        # Creer la tache d'emargement automatique
        $action = New-ScheduledTaskAction -Execute "pythonw" -Argument "$scriptPath"
        $trigger = New-ScheduledTaskTrigger -At $emargementTime -Once
        try {
            Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description "Tache d'emargement automatique"
            Write-Host "Tache planifiee pour emargement a $emargementTime creee." -ForegroundColor Green
        } catch {
            Write-Host "Erreur lors de la creation de la tache d'emargement : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Tache d'emargement pour $taskName existe deja." -ForegroundColor Yellow
    }
}

# Trouver le premier cours de la semaine suivante (Jour +7)
$nextWeekStart = $today.AddDays(7)
$firstCourseTime = $courseTimes | Where-Object { $_.Date -eq $nextWeekStart.Date } | Sort-Object | Select-Object -First 1

if ($firstCourseTime -ne $null) {
    $analysisTime = $firstCourseTime.AddHours(1) # Ajouter 1 heure au premier cours

    # Planifier une tache d'analyse pour la semaine suivante
    $analysisTaskName = "AnalyseCours_$($nextWeekStart.ToString('yyyyMMdd'))"
    if (-not (Get-ScheduledTask -TaskName $analysisTaskName -ErrorAction SilentlyContinue)) {
        $analysisTrigger = New-ScheduledTaskTrigger -At $analysisTime -Once

        # Modifier ici pour s'assurer que la fenêtre est cachée
        $analysisAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -File `"$PSCommandPath`""

        try {
            Register-ScheduledTask -Action $analysisAction -Trigger $analysisTrigger -TaskName $analysisTaskName -Description "Analyse des cours de la semaine prochaine"
            Write-Host "Tache d'analyse planifiee pour $analysisTime." -ForegroundColor Green
        } catch {
            Write-Host "Erreur lors de la creation de la tache d'analyse : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "La tache d'analyse existe deja." -ForegroundColor Yellow
    }
} else {
    Write-Host "Aucun cours trouve le jour +7 pour planifier l'analyse." -ForegroundColor Yellow
}

Write-Host "Toutes les taches planifiees ont ete verifiees et mises a jour." -ForegroundColor Cyan

# Arret de l'enregistrement du journal
Stop-Transcript

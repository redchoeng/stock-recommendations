# 관리자 권한 필요
# PowerShell을 관리자 권한으로 실행 후 이 스크립트 실행

$TaskName = "주식리포트_1시간마다_업데이트"
$ScriptPath = "$PSScriptRoot\자동_업데이트_1시간마다.bat"

# 기존 작업이 있으면 삭제
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 트리거: 매 1시간마다
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)

# 액션: 배치 파일 실행
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`""

# 설정
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 작업 등록
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -Description "1시간마다 주식 추천 리포트 자동 업데이트"

Write-Host "작업 스케줄러 등록 완료!" -ForegroundColor Green
Write-Host "작업 이름: $TaskName" -ForegroundColor Cyan
Write-Host "실행 주기: 매 1시간마다" -ForegroundColor Cyan
Write-Host ""
Write-Host "확인 방법: 작업 스케줄러(taskschd.msc)에서 확인 가능" -ForegroundColor Yellow

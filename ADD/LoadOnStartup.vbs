Option Explicit

Dim objShell, objFSO
Dim scriptPath, targetPath, shortcutPath, startupFolder

' Получаем путь к текущей папке скрипта
Set objFSO = CreateObject("Scripting.FileSystemObject")
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Путь к CatPilot.exe
targetPath = objFSO.BuildPath(scriptPath, "CatPilot.exe")

' Проверяем существование файла CatPilot.exe
If Not objFSO.FileExists(targetPath) Then
    MsgBox "Ошибка: Файл CatPilot.exe не найден в папке:" & vbCrLf & scriptPath, vbCritical, "Ошибка"
    WScript.Quit(1)
End If

' Получаем путь к папке автозагрузки текущего пользователя
Set objShell = CreateObject("WScript.Shell")
startupFolder = objShell.SpecialFolders("Startup")

' Создаём путь для ярлыка
shortcutPath = objFSO.BuildPath(startupFolder, "CatPilot.lnk")

' Создаём ярлык
Dim objShortcut
Set objShortcut = objShell.CreateShortcut(shortcutPath)
objShortcut.TargetPath = targetPath
objShortcut.WorkingDirectory = scriptPath
objShortcut.Save
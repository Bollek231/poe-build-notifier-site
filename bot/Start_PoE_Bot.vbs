Option Explicit
Dim sh, fso, folder, pythonExe, command
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
pythonExe = folder & "\.venv\Scripts\pythonw.exe"
If fso.FileExists(pythonExe) Then
    sh.CurrentDirectory = folder
    sh.Run """" & pythonExe & """ """ & folder & "\launcher.pyw""", 0, False
Else
    sh.Run """" & folder & "\Start_PoE_Bot.bat""", 1, False
End If

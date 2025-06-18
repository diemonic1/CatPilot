Dim WShell
Set WShell = CreateObject("WScript.Shell")

Set args = Wscript.Arguments
WShell.Run args(0)

Set WShell = Nothing

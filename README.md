# CatPilot <img src="https://github.com/diemonic1/CatPilot/blob/main/CatPilot.ico?raw=true" width="80" />

![Static Badge](https://img.shields.io/badge/diemonic1-CatPilot-CatPilot)
![GitHub top language](https://img.shields.io/github/languages/top/diemonic1/CatPilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub Repo stars](https://img.shields.io/github/stars/diemonic1/CatPilot)
![GitHub issues](https://img.shields.io/github/issues/diemonic1/CatPilot)

[Documentation on english](#Documentation-on-english)

[Документация на русском языке](#Документация-на-русском-языке)

# Documentation on english
This program allows you to control Windows using VBS scripts via a local network or public IP (similar to webhooks), or using a telegram bot.

[Installation](#Installation)

[How to write scripts](#How-to-write-scripts)

[Emulating keystrokes](#Emulating-keystrokes)

[Ready-made script examples](#Ready-made-script-examples)

[Integration with a telegram bot](#Integration-with-a-telegram-bot)

[Quick link opening](#Quick-link-opening)

[Control outside the local network (Yandex Alice, IFTTT, etc.)](#control-outside-the-local-network-yandex-alice-ifttt-etc)

[URL of an additional request](#URL-of-an-additional-request)

[Program update](#Program-update)

[Developer information: additional localizations](#Developer-information-additional-localizations)

[Developer information: how to build the program](#Developer-information-how-to-build-the-program)

## Installation
Download the current build version on [page releases](https://github.com/diemonic1/CatPilot/releases)

Unzip the CatPilot folder anywhere and run CatPilot.exe

## How to write scripts
VBS allows you to implement most useful scripts. Here is a common template for a script:

```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("")
```

With WShell.Run("") you can run any commands, including .bat scripts, python scripts or just cmd commands.

> [!TIP]
> To prevent a python script from showing the console when running, but to run it in the background, simply rename the ScriptName.py script file to ScriptName.pyw, changing the extension

You can use the ' symbol to indicate a comment inside VBS

Comments will be highlighted in color in the editor.

You can use any UTF-8 characters as a script name, including text emoticons 😻.

The script URL can only consist of Latin characters and numbers. The names or URLs of two different scripts cannot be duplicated.

You can launch the script execution by URL.

### Example
I create a script with URL="RunNotepad" and the name "📄 Run Notepad 📄":
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("notepad.exe")
```

> [!TIP]
> Scripts, names and URLs can be pasted and copied if English input is enabled

The IP address of my computer in the local network is 192.168.0.102, which means I can run the script by creating a GET request (opening it in a browser, for example) to 192.168.0.102:5000/RunNotepad
After that, my notepad will open.

> [!IMPORTANT]
> Your router can dynamically assign IP addresses to devices, so - to avoid changing the link you run commands from every time - either disable dynamic allocation in its settings, or assign a specific IP to your device

## Emulating keystrokes
You can add keys to each script that will be emulated during its execution. For example, by selecting the "f5" key, you can emulate pressing it:
| f5 |
|:-----|
| + |
| None |
| + |
| None |

By specifying several keys, you can call a keyboard shortcut. For example, ctrl+shift+escape will call the task manager (keystrokes will be emulated):
| ctrl |
|:-------|
| + |
| shift |
| + |
| escape |

> [!TIP]
> If you don't need a script, but only emulation of keys, you can insert only a comment inside the script, for example 'only buttons click
## Ready-made script examples
### Run a program with spaces in the path
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run Chr(34) & "C:\Program Files (x86)\Steam\steam.exe"
```
### Kill some program (for example FxSound.exe)
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "taskkill /F /IM FxSound.exe", 0
```
### Run a python script
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("C:\Programs\Test\Check.pyw")
```
### Open page in browser
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "https://www.google.com/"
```
### Restart PC
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "shutdown.exe -r -f -t 00"
```
### Shutdown computer
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "shutdown.exe /s /t 5"
```
### Put computer to sleep
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "rundll32.exe powrprof.dll,SetSuspendState Sleep"
```
### Run two programs and open a website
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run Chr(34) & "C:\Program Files (x86)\Steam\steam.exe" 'open steam
WShell.Run("S:\Oculus\Support\oculus-client\OculusClient.exe") 'open oculus client

WShell.Run "https://www.google.com/"
```
### Empty script with a comment
```
'comment
```
### Next track/video
| nexttrack |
|:----------|
| + |
| None |
| + |
| None |

### Previous track/video
| prevtrack |
|:----------|
| + |
| None |
| + |
| None |

### Increase volume
| volumeup |
|:---------|
| + |
| None |
| + |
| None |

### Decrease volume
| volumedown |
|:-----------|
| + |
| None |
| + |
| None |

### Pause media
| playpause |
|:----------|
| + |
| None |
| + |
| None |

## Integration with a telegram bot
You can also execute commands using a telegram bot. When sending commands this way, you do not need to be on the same local network as the device.
First, you need to create your own telegram bot. You can name it whatever you like, for example, 🐾 CatPilot 🐾, and upload a cat as an avatar:

<img src="https://github.com/diemonic1/CatPilot/blob/main/CatPilot.png" width="250" />

After creating the bot, you will receive its token (for example 4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc)

- Paste this token into the CatPilot settings

The bot will execute commands only from those users whose telegram IDs are specified in the settings in the allowed list.
You can find out your telegram ID from this bot [@getmyid_bot](https://t.me/getmyid_bot)

The ID must be written with a comma, without spaces: 45435345,12356567

You can get a list of commands in the bot using any of these messages: /start /help /commands /начать /помощь /команды

> [!TIP]
> You can run commands from the TG bot by sending it a message with the name or URL of the command (without having to call the list with all the commands).

After a while, the program will delete the message with the list of commands so that you do not accidentally run some command that no longer exists (you can always click on the last message to repeat the execution, including the output of commands).

## Quick link opening
If you have connected the bot, you can use the quick link opening. If you send the bot a message that contains http, https or .com, it will open the link in a standard browser.

> [!TIP]
> Using quick link opening, you can, for example, click "share video" in the YouTube mobile app and send the link to it to the bot, and then it will immediately open it on the computer

## Control outside the local network (Yandex Alice, IFTTT, etc.)
You can execute commands even when you are not on the same local network as the device.
This may be necessary if you want to control the computer using Yandex Alice, IFTTT or another service that supports webhooks.

If you have a white IP address, you can forward ports (keep in mind that this is not safe).

An alternative would be to use services like ngrok, cloudpub, Tuna or any other similar ones that allow you to create a tunnel.

To integrate with Yandex Alice, you can use the "Domovenok Kuzya" skill.

### Restarting a tunnel in case of an error

If the application you are using to create a tunnel is unstable and sometimes loses connection, you can restart it. To do this, create a script called RestartTunnel.vbs (with this exact name) inside the CatPilot application folder and write the code that restarts your tunnel into it.

In my case the code looks like this:
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "taskkill /f /im clo.exe", 0
WShell.Run "S:\Programs\CatPilot\StartTunnel.bat", 0
```

> Here the clo.exe process is closed, after which the .bat file is launched, restarting the tunnel with my token:
```
clo.exe set token 0cWE3Zmrdrmvp6B_QtSzXDTb0sRntiPDE5G_f4vtuAw
clo.exe publish http 192.168.0.137:5000
clo.exe run
```

In the CatPilot settings, specify the link by which CatPilot can be accessed outside the local network.
> because I use cloudpub, for me this link looks like https://mydomen.cloudpub.ru/Call
>
> you will have your own domain, but /Call should also be present - this is a standard request for the CatPilot application

Your https://example.yourservice.com/Call will be requested every minute, expecting to receive a 200 "Ok" response
If no response is received, the RestartTunnel.vbs script will be launched

If the script does not exist, or if the link is not specified, this code will not work.

If the script and link are specified, the RestartTunnel.vbs script will be launched when CatPilot starts (this way you can automatically start your tunnel)

## URL of an additional request
You may need to track whether CatPilot is currently running or not. To do this, you can request https://example.yourservice.com/Call yourself, or use the additional URL function.
If you specify an additional request URL in the CatPilot settings, a GET request will be sent to this URL every minute. This way, you can, for example, send a GET request to the server to track whether the program is still running and working (or whether the computer is working in general, if the program is always active while it is on).

## Program update
1) Download the new version as a zip archive, unzip the CatPilot folder from it
2) Kill the CatPilot process (via the program itself or via the task manager)
3) Move all files from the CatPilot folder of the new version to the folder where you have CatPilot installed, confirm the replacement of all files (settings, scripts and log will not be replaced)
4) Run CatPilot again

> [!NOTE]
> If, when replacing files, the system indicates that the VCRUNTIME140.dll or VCRUNTIME140_1.dll files are occupied by another process, simply skip replacing them, they are not necessary.

## Developer information: additional localizations
The Localization folder stores json files with localized text. You can create a new localization file by specifying the language as the file name and filling in the translation inside (based on the English localization, for example).

After restarting the program, localization can be selected in the settings.

> [!IMPORTANT]
> Please note that localization keys cannot be changed.

## Developer information: how to build the program
To build an exe application, use pyinstaller.exe

If you want to somehow modify the program, you need to change the python file CatPilot.py - it contains all the code.

After that:
1) Open the console as administrator in the folder where CatPilot.py is located
2) Run the command:
```pyinstaller.exe —onedir —icon=CatPilot.ico —windowed CatPilot.py```
3) After the build is complete, the CatPilot folder will appear in the dist folder, this is the finished build
4) Copy all the contents from the ADD folder to the CatPilot folder, which contains the build (these are additional files of libraries, scripts, localizations, etc., necessary for the program to work)
5) Now the program can be launched as usual using CatPilot.exe

# Документация на русском языке
Это программа позволяет управлять Windows посредством VBS скриптов через локальную сеть или публичный IP (на подобии webhooks), или с помощью телеграмм бота.

[Установка](#Установка)

[Как писать скрипты](#Как-писать-скрипты)

[Эмуляция нажатий клавиш](#Эмуляция-нажатий-клавиш)

[Готовые примеры скриптов](#Готовые-примеры-скриптов)

[Интеграция с телеграмм ботом](#Интеграция-с-телеграмм-ботом)

[Быстрое открытие ссылки](#Быстрое-открытие-ссылки)

[Управление вне локальной сети (Яндекс Алиса, IFTTT и т.д.)](#управление-вне-локальной-сети-яндекс-алиса-ifttt-и-тд)

[URL дополнительного запроса](#URL-дополнительного-запроса)

[Обновление программы](#Обновление-программы)

[Информация для разработчиков: дополнительные локализации](#Информация-для-разработчиков-дополнительные-локализации)

[Информация для разработчиков: как собрать билд программы](#Информация-для-разработчиков-как-собрать-билд-программы)

## Установка
Скачайте актуальную версию билда на [странице релизов](https://github.com/diemonic1/CatPilot/releases)

Распакуйте папку CatPilot куда угодно и запустите CatPilot.exe

## Как писать скрипты   
VBS позволяет реализовать большинство полезных скриптов. Вот обыкновенный шаблон для скрипта:   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("")
```
   
С помощью WShell.Run("") можно запускать любые команды, в том числе и выполнение .bat скриптов, пайтон скриптов или просто команд для cmd.   

> [!TIP]
> Чтобы при запуске пайтон скрипт не показывал консоль, а исполнялся в фоне, достаточно переименовать файл скрипта ScriptName.py в ScriptName.pyw, изменив расширение   
   
Для обозначения комментария внутри VBS можно использовать символ '   
Комментарии будут выделяться цветом в редакторе.  
   
В качестве имени скрипта вы можете использовать любые символы UTF-8, в том числе и текстовые смайлики 😻.   
   
URL скрипта может состоять только из латинских символов и цифр. Имена или URL двух разных скриптов дублироваться не могут.   
   
Именно по URL вы можете запустить выполнение скрипта.   
   
### Пример   
Я создаю скрипт с URL="RunNotepad" и именем "📄 Запустить блокнот 📄":   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("notepad.exe")
```
   
> [!TIP]
> Скрипты, имена и URL можно вставлять и копировать, если включен ввод на английском языке

IP адрес моего компьютера в локальной сети - 192.168.0.102, значит, запустить скрипт я могу создав GET-запрос (открыв в браузере, например) к 192.168.0.102:5000/RunNotepad   
После этого у меня откроется блокнот.   

> [!IMPORTANT]
> Ваш роутер может динамически присваивать устройствам IP адреса, поэтому - чтобы не менять каждый раз ссылку, по который вы запускаете команды - либо отключите динамическое распределение в его настройках, либо закрепите за своим устройством конкретный IP   
   
## Эмуляция нажатий клавиш
К каждому скрипту вы можете добавить клавиши, которые будут эмулироваться во время его выполнения. Например, выбрав клавишу "f5" можно эмулировать ее нажатие:  
|   f5 |
|:-----|
|    + |
| None |
|    + |
| None |

Задав несколько клавиш, можно вызвать клавишное сочетание. Например, ctrl+shift+escape вызовет диспетчер задач (будет эмулироваться зажатие клавиш):   
|   ctrl |
|:-------|
|      + |
|  shift |
|      + |
| escape |

> [!TIP]
> Если вам нужен не скрипт, а только эмуляция клавиш, вы можете вставить внутрь скрипта только комментарий, например 'only buttons click   
## Готовые примеры скриптов
### Запустить программу, в пути до которой есть пробелы   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run Chr(34) & "C:\Program Files (x86)\Steam\steam.exe"
```
### Убить какую-нибудь программу (например FxSound.exe)   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "taskkill /F /IM FxSound.exe", 0
```
### Запустить скрипт пайтон   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("C:\Programs\Test\Check.pyw")
```
### Открыть страницу в браузере   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "https://www.google.com/"
```
### Перезапустить ПК   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "shutdown.exe -r -f -t 00"
```
### Выключить компьютер   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "shutdown.exe /s /t 5"
```
### Усыпить компьютер   
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "rundll32.exe powrprof.dll,SetSuspendState Sleep"
```
### Запустить две программы и открыть сайт  
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run Chr(34) & "C:\Program Files (x86)\Steam\steam.exe" 'open steam
WShell.Run("S:\Oculus\Support\oculus-client\OculusClient.exe") 'open oculus client

WShell.Run "https://www.google.com/"
```
### Пустой скрипт с комментарием
```
'comment
```
### Следующий трек/видео   
| nexttrack |
|:----------|
|         + |
|      None |
|         + |
|      None |

### Предыдущий трек/видео   
| prevtrack |
|:----------|
|         + |
|      None |
|         + |
|      None |

### Увеличить громкость   
| volumeup |
|:---------|
|        + |
|     None |
|        + |
|     None |

### Уменьшить громкость   
| volumedown |
|:-----------|
|          + |
|       None |
|          + |
|       None |

### Поставить медиафайл на паузу   
| playpause |
|:----------|
|         + |
|      None |
|         + |
|      None |

## Интеграция с телеграмм ботом
Вы также можете выполнять команды с помощью телеграмм бота. При отправке команд таким образом не обязательно находиться в одной локальной сети с устройством.
Для начала необходимо создать собственного телеграмм бота. Можете назвать его как угодно, например, 🐾 CatPilot 🐾, и загрузить в качестве аватарки котика:

<img src="https://github.com/diemonic1/CatPilot/blob/main/CatPilot.png" width="250" />

После создания бота вы получите его токен (например 4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc)

- Вставьте этот токен в настройки CatPilot

Бот будет выполнять команды только тех пользователей, чьи телеграмм ID указаны в настройках в списке разрешенных. 
Узнать ваш телеграмм ID вы можете у этого бота [@getmyid_bot](https://t.me/getmyid_bot)

ID нужно записывать через запятую, без пробелов: 45435345,12356567

В боте можно получить список команд с помощью любого из этих сообщений: /start /help /commands /начать /помощь /команды 

> [!TIP]
> Можно запускать команды из тг бота, присылая ему сообщение с именем или URL команды (без необходимости вызова списка со всеми командами).

Через некоторое время программа удалит сообщение со списком команд, чтобы вы случайно не запустили какую-то несуществующую к этому моменту команду (вы всегда можете нажать на последние сообщение, чтобы повторить выполнение, в том числе вывод команд).

## Быстрое открытие ссылки
Если вы подключили бот, вы можете воспользоваться быстрым открытием ссылки. Если вы отправите боту сообщение, которое содержит http, https или .com, он откроет ссылку в стандартном браузере.

> [!TIP]
> Используя быстрое открытие ссылки, вы можете, например, нажать в мобильном приложении YouTube "поделиться видео" и отправить ссылку на него боту, и тогда он сразу откроет его на компьютере

## Управление вне локальной сети (Яндекс Алиса, IFTTT и т.д.)
Вы можете выполнять команды и не находясь в одной локальной сети с устройством.
Это может понадобиться, если вы хотите управлять компьютером с помощью Яндекс Алисы, IFTTT или другого сервиса, поддерживающего webhooks.

Если у вас белый IP адрес, вы можете пробросить порты (учтите, что это не безопасно).

Альтернативой будет использование сервисов на подобии ngrok, cloudpub, Tuna или любых других аналогов, позволяющих создать туннель.

Для интеграции с Яндекс Алисой можно воспользоваться навыком "Домовенок Кузя".

### Перезапуск туннеля в случае ошибки

Если приложение, с помощью которого вы создаете туннель, работает нестабильно и иногда теряет связь, вы можете его перезапускать. Для этого создайте внутри папки приложения CatPilot скрипт RestartTunnel.vbs (именно с таким названием) и запишите в него код, который перезапускает ваш туннель.

В моем случае код выглядит так:
```
Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run "taskkill /f /im clo.exe", 0
WShell.Run "S:\Programs\CatPilot\StartTunnel.bat", 0
```

> Здесь закрывается процесс clo.exe, после чего запускается .bat файл, заново запускающий туннель с моим токеном:
```
clo.exe set token 0cWE3Zmrdrmvp6B_QtSzXDTb0sRntiPDE5G_f4vtuAw
clo.exe publish http 192.168.0.137:5000
clo.exe run
```

В настройках CatPilot укажите ссылку, по которой к CatPilot можно обратиться вне локальной сети.
> т.к. я использую cloudpub, у меня эта ссылка выглядит как https://mydomen.cloudpub.ru/Call
> 
> у вас будет свой домен, но /Call тоже должно присутствовать - это стандартный запрос для приложения CatPilot

Ваш https://example.yourservice.com/Call будет запрашиваться ежеминутно, ожидая получить ответ 200 "Ok"
Если ответ не будет получен, запуститься скрипт RestartTunnel.vbs

Если скрипт не существует, или если ссылка не указана, этот код работать не будет.

Если скрипт и ссылка указаны, скрипт RestartTunnel.vbs будет запускаться при старте CatPilot (так вы можете автоматически запускать ваш туннель)

## URL дополнительного запроса
Вам может понадобиться отслеживать, работает ли в данный момент CatPilot или нет. Для этого вы можете сами самостоятельно запрашивать https://example.yourservice.com/Call, либо же воспользоваться функцией дополнительного URL.
Если указать в настройках CatPilot URL дополнительного запроса, каждую минуту на этот URL будет осуществляться GET запрос. Таким образом можно, например, отправлять GET запрос на сервер, чтобы отслеживать, что программа все еще запущена и работает (или же в целом работает компьютер, если программа активна всегда, пока он включен).

## Обновление программы
1) Скачайте новую версию в виде zip архива, распакуйте из него папку CatPilot 
2) Убейте процесс CatPilot (через саму программу или через диспетчер задач)
3) Переместите все файлы из папки CatPilot новой версии в папку, где у вас установлен CatPilot, подтвердите замену всех файлов (настройки, скрипты и лог заменяться не будут)
4) Запустите CatPilot заново
   
> [!NOTE]
> Если при замене файлов система укажет, что файлы VCRUNTIME140.dll или VCRUNTIME140_1.dll заняты другим процессом, просто пропустите их замену, они не обязательны.

## Информация для разработчиков: дополнительные локализации
В папке Localization хранятся json файлы с локализированным текстом. Вы можете создать новый файл локализации, указав в качестве названия файла язык, и заполнив внутри перевод (основываясь на английской локализации, например).

После перезапуска программы локализацию можно будет выбрать в настройках.

> [!IMPORTANT]
> Обратите внимание, что ключи локализации изменяться не могут.

## Информация для разработчиков: как собрать билд программы
Для сборки exe приложения используется pyinstaller.exe

Если вы хотите как-то модифицировать программу, вам необходимо изменять python файл CatPilot.py - в нем содержится весь код.

После этого:
1) Откройте консоль от имени администратора в папке, в которой лежит CatPilot.py
2) Выполните команду:
```pyinstaller.exe —onedir —icon=CatPilot.ico —windowed CatPilot.py```
3) После окончания сборки в папке dist появится папка CatPilot, это готовая сборка
4) Скопируйте из папки ADD все содержимое в папку CatPilot, в которой находится сборка (это дополнительные файлы библиотек, скриптов, локализаций и т.д., нужных для работы программы)
5) Теперь программу можно как обычно запускать с помощью CatPilot.exe

<details>
<summary>SEO tags</summary>
Программа для управления Windows удаленно,автоматизация Windows через скрипты, управление компьютером удалённо, автоматизация компьютера, сценарии для управления ПК, управление компьютером через VBS скрипты, аналоги Laitis, управление компьютером через телеграмм бота,удаленный доступ к компьютеру, Program for remote Windows management, Windows automation via scripts, remote computer management, computer automation, scripts for PC management, computer management via VBS scripts, Laitis analogs, computer management via telegram bot, remote access to computer
</details>

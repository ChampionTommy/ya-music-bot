<div align="center">
	<br />
	<p>
		<img src="https://yandex.ru/support/music/docs-assets/support-music-tld-ru/rev/r17958544/ru/_assets/logo/on-black-yellow-ru.png" width="400" alt="yandex music" />
	</p>
	<br />
    <p>
        <a href="https://pypi.org/project/discord.py/"><img src="https://img.shields.io/pypi/v/discord.py.svg?maxAge=3600" alt="PyPI version" /></a>
        <a href="https://pypi.org/project/discord.py/"><img src="https://img.shields.io/pypi/dm/discord.py.svg?maxAge=3600" alt="PyPI downloads" /></a>
        <a href="https://github.com/Rapptz/discord.py/commits/master"><img src="https://img.shields.io/github/last-commit/Rapptz/discord.py.svg?logo=github&logoColor=ffffff" alt="Last commit." /></a>
        <a href="https://pypi.org/project/yandex-music/"><img src="https://img.shields.io/pypi/v/yandex-music.svg?maxAge=3600" alt="Yandex.Music API version" /></a>
    </p>
</div>

# Discord Music Bot (Яндекс Музыка)

## Что это?

Это бот для Discord, который воспроизводит треки из **Яндекс Музыки**.  На данный момент это альфа версия. Чарт может работать с задержкой
плейлисты только от определенных пользователей запускаются (YM не дает  открытый json при запуске плейлиста, даже при авторизации, а в api нет функционала, только допиливать)
Поддерживаются команды для проигрывания треков, альбомов, плейлистов, чарта России, паузы, пропуска и остановки воспроизведения.  

## Features

- Воспроизведение треков по ссылке или поисковому запросу  
- Поддержка альбомов, плейлистов и чарта России  
- Очередь треков и управление очередью (`play`, `queue`, `skip`, `stop`, `nowplaying`)  
- Поддержка голосовых каналов Discord  
- Работа с локальными файлами для стабильного воспроизведения  
- Обработка ошибок API Яндекс Музыки  

## Requirements

Для стабильной работы бота рекомендуется:  

- **Операционная система:** Ubuntu / Debian (Linux)  
- **Python:** 3.12  
- **CPU:** 1 ядро достаточно  
- **RAM:** минимум 2 ГБ  
- **FFMPEG**
- **Установленные пакеты:**  
```text
aiofiles==23.1.0
aiohttp==3.13.2
aiosignal==1.4.0
attrs==23.1.0
certifi==2023.7.22
cffi==1.15.1
charset-normalizer==3.2.0
discord.py==2.6.4
frozenlist==1.8.0
idna==3.5
multidict==6.0.4
pycparser==2.21
PyNaCl==1.5.0
PySocks==1.7.1
python-dotenv==1.0.0
requests==2.31.0
urllib3==2.0.4
yandex-music==2.0.1
yarl==1.22.0
```
## Install venv
`
python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
`python main.py`

## .env

Необходимо в корне создать файл `.env` и указать там yandex music tokern & discord bot token + prefix для команд.

```
DISCORD_BOT_TOKEN=
YANDEX_MUSIC_TOKEN=
DISCORD_BOT_COMMAND_PREFIX=
```

## commands

### запуск альбома
`/queue https://music.yandex.ru/album/<id>`
### запуск чарта (запуск треков +- 1 минута)
`/chart`
### запуск артиста
`/artist https://music.yandex.ru/artist/<id artist>`
### запуск трека
`/play https://music.yandex.ru/album/<id artist>/track/<id track>`

### при альбоме или плейлисте работает перелистывание треков
`/skip`


## etc

Запускатеся на windows и linux, главное установить зависимости, например на win просит gcc+ и доп компиляторы.
В дальнейшем хотелось бы добавить "своя волна", "мне нравится" и "плейлисты рандомные"

на 1 ядре cpu загружено на 5%, нагрузки никакой нет.
Хотел написать про daemon systemd, но настраивайте сами, chatgpt в помощь. Возможно закину docker на alpine.

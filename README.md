## Установка программы
Для того чтобы воспользоваться программой, у Вас должен быть установлен интерпретатор **Python** и среда разработки (IDE) на Вашем компьютере. Чтобы установить их, пожалуйста, внимательно прочитайте инструкцию по их установке [здесь](https://github.com/serovaolesya/sci_papers_translationese/blob/main/README_HOW_TO_INSTALL_PYHTHON.md) и выполните все описанные в ней шаги.

### Инструкция для пользователей, у которых есть опыт работы с github

**1.** Клонируйте репозиторий на свой компьютер:
    
    git clone git@github.com:serovaolesya/sci_papers_translationese.git
**2.** Откройте склонированный проект в любом IDE и обязательно установите виртуальное окружение:


Команда для Windows:

    python -m venv venv
    
Команда для Linux и macOS:

    python -m venv venv

После выполнения этой команды в директории проекта появится папка venv (от virtual environment, «виртуальное окружение»), в ней хранятся служебные файлы. В этой же директории будут сохраняться все зависимости библиотеки и модули, используемые в приложении.

**3.** Активируйте виртуальное окружение. Для этого, находясь в корневой директории проекта, введите в терминал команду:

Команда для Windows:

    source venv/Scripts/activate
или

    venv/Scripts/activate


Для Linux и macOS:

     source venv/bin/activate

**4.** **Обязательно** установите зависимости приложения, без них оно работать не будет:

Из корневой директории проекта введите следующую команду:

    pip install -r requirements.txt


### Инструкция для пользователей без опыта работы с github

**1.** Скачайте ZIP-архив с программой [по этой ссылке](https://github.com/serovaolesya/sci_papers_translationese/archive/refs/heads/main.zip)

**2.** Распакуйте ZIP-архив с репозиторием, откройте IDE (об установке Python и IDE можно прочитать [здесь](https://github.com/serovaolesya/sci_papers_translationese/blob/main/README_HOW_TO_INSTALL_PYHTHON.md)). Мы рекомендуем воспользоваться бесплатной версией IDE
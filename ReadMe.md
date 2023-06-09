# Проект OTUS - Python Developer Professional
## Тема: Telegram-бот "Спаси сову" по спасению редких животных в Москве

Суть проекта: Настроить коммуникацию между жителями Москвы и Департаментом природопользования и охраны окружающей среды Москвы используя Telegram бота

Ссылка на бота 🦉: https://t.me/Msk_animalsave_bot  
Ссылка на официальный анонс: https://t.me/kgh_moscow/10506

Проект реализован с помощью двух ботов:  
1. public_bot - данный бот позволяет заполнить форму с указанием Адреса, Вида животного, Количества животных, Фото/Видео материалов и контактов (по желаю). После заполнения всех обязательных полей, пользователь направляет введенные данные операторам, которые мониторят второго бота
2. private_bot - админский бот, который имеет две функции:
- Панель операторов. В нее поступают обращения пользователей, на которые оператор реагирует в режиме реального времени (данные обращения параллельно отправляются в общий-закрытый канал - а-ля логирование). У операторов есть опции "Взять в работу", "Отклонить", "Заблокировать"
- Админская панель. Супер-админы, которые назначают операторов и следят за их действиями.

report.py - автоматическая генерация отчетности по количеству подписавшихся пользователей и отработанным обращениям

Схема диалогов telegram бота "Спаси сову"

![Image alt](https://github.com/EugeniyGA/save_owl_bot/blob/main/Scheme_of_dialogues_of_telegram-bot_Save_owl_Moscow.jpg)

# Disclaimer

Этот код не предназначен для развертывания другими пользователями. Это специализированный проект, предназначенный для конкретного приложения. Однако вы можете изучить код, чтобы понять, как выполняется реализация. Обратите внимание, что может потребоваться некоторая конфигурация или изменения, чтобы адаптировать код для других проектов или целей.

Этот проект представляет собой уникальную реализацию телеграмм-ботов для общественного блага, и его основная функция — способствовать спасению исчезающих животных в Москве. Это достигается путем предоставления оптимизированного канала связи между жителями и соответствующим отделом охраны окружающей среды.

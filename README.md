# ДЗ 4. Асинхронные интеграции

## Запуск проекта и тестов
Чтобы запустить приложение, нужно выполнить следующую
команду:
```bash
make run
```
Далее переходим по http://localhost:8000.

Для запуска тестов необходимо выполнить 
следующую команду: 
```bash
make test
```

Запустив и протестировав приложение,
можно очистить использованные ресурсы.
Остановим и удалим контейнеры:
```bash
docker-compose down --volumes
```
>*Примечание:* флаг `--volumes` позволяет удалять
> **именованные** тома. В данном проекте это 
> `pgdata`. Удалять именованные тома нужно хотя
> бы потому, что скрипт инициализации `init_db_script.sql`,
> создающий таблицу при запуске контейнера 
> postgres, выполняется **только** если база данных
> у контейнера пустая.

Удалим все образы: 
```bash
docker rmi $(docker images -q) --force
```
>*Примечание:* будут удалены образы, 
> созданные не только с помощью `docker-compose`.
> Так что осторожнее!

## Документация о проделанной работе
### 1. Настройка проекта для работы с Celery
Проект был создан с помощью **FastAPI**.
Пользователь нажимает на кнопку `Create Task!`,
чтобы создать "задачу",
после чего происходит вызов `time.sleep()`, 
имитирующий выполнение длительной операции.
Активные и Завершенные задачи отображаются 
на главной странице.
### 2. Создание асинхронной задачи Celery
Так как проект включает в себя только одно 
приложение, для простоты и конфигурация 
Celery, и Celery
tasks задаются в одном файле `celery.py`.
В этот файл переносится имитация длительной задачи:
```python
@celery.task
def user_task(should_fail: bool):
    sleep(7)
    if should_fail:
        raise ValueError("An error occurred in user_task")
    return True
```
Функция принимает на вход `should_fail`, 
определяющий, завершится ли успешно 
имитируемая задача.
### 3. Реализация эндпоинта для задачи
Нажатие на кнопку `Create Task!`
создаёт POST-запрос по адресу
`/submit`. Обработка запроса 
происходит в следующей ручке:
```python
@app.post("/submit", response_class=HTMLResponse)
async def handle_form(request: Request):
    should_fail: bool = random.choice([True, False])
    new_task = user_task.delay(should_fail)
    active_tasks.add(new_task)
    return templates.TemplateResponse(
        request=request, name="task_created.html", context={"new_task": new_task}
    )
```
Задача отправляется на выполнение
Celery worker'у, а пользователю
моментально возвращается
ответ. С шансом 50% задача будет провалена.

### 4. Отслеживание статуса задачи
Нажатие на кнопку `Check Status` посылает 
GET-запрос по адресу `/get-status/{идентификатор
задачи}`. Здесь можно обновлять статус задачи
с помощью `Refresh Status`, а когда состояние
сменится с `PENDING`, можно вернуться 
обратно, нажав `Return Back`.
### 5. Сохранение результата задачи после выполнения
Активные задачи (`PENDING`) хранятся в 
оперативной памяти, во множестве `active_tasks`.
При каждом GET-запросе на адрес `/` из
множества активных задач удаляются задачи, 
успевшие завершиться. При завершении 
задачи с помощью Celery сигнала вызывается
Celery Task `task_postrun_handler`, сохраняющий
результат выполнения задачи и статус завершения
в БД:
```python
@task_postrun.connect(sender=user_task)
def task_postrun_handler(sender, task_id, task, args, kwargs, retval, state, **kw):
    if state == 'SUCCESS':
        result = retval
    else:
        result = str(retval)
    insert_task(task_id, result, state)
```
### 6. Unit-тесты для асинхронной задачи
Чтобы не отправлять задачу в брокер, 
будем вызывать задачу напрямую
с помощью метода
`run`. Чтобы тесты не 
проходили слишком долго, замокаем `sleep`.
Протестируем успешное и неуспешное выполнение
задачи:
```python
def test_user_task_success():
    with patch('src.celery.sleep') as mock_sleep:
        result = user_task.run(False)
        assert result is True
        mock_sleep.assert_called_once_with(7)


def test_user_task_failure():
    with patch('src.celery.sleep'):
        with pytest.raises(ValueError):
            user_task.run(True)
```

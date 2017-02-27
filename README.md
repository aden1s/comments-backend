# comments-backend
Example of backend API

Backend для работы с иерархическими комментариями
=================================================

API для работы с комментариями. Добавление, удаление, редактироване, чтение истории, выгрузка в файл.
Приложене написано на основе Django REST Framework, в качестве базы данных используется PostgreSQL, как временное хранилище
для истории используется Redis.

Хранение комментариев организовано в таблице Comments, для сохранения иерархии использован Materialized Path,что позволяет гибко
хранить полный путь. Для хранения используется тип данных Array, а на стороне Django поддерживается в django.contrib.postgres.fields. Путь хранится в ввиде массива идентификаторов.

Для преобразования из "линейного вида" БД в иерархическую структуру используется следующий класс MaterializedPathConvert
```python
from comments.utils import MaterializedPathConvert
```

Временные данные и истории выгрузок хранятся в файле, а сама история (время + ссылка на файл) хранится в Redis.
Теоретически лучше отказаться от хранения истории в файле и перенести в кеш (как вариант тот же redis)

Функционал создания, редактирования, удаления, изменения покрыт тестами. 
Также можно предзагрузить небольшое количество данных командой preload


Основные функции
----------------

Добавление комментария первого уровня для сущности 3/3 [POST]:
```python 
from django.urls import reverse

from rest_framework.test import APIClient

data = {'entity_id': 3, "entity_type": 3, "comment": "Comment level INIT", "user": 1}
client.post('/create/', data, format="json")
```
Изменение комментария по ID [PUT]:
```python
url = reverse('comment-item', kwargs={"pk": 1})
response = client.put(url, {"comment":"Changed comment"}, format='json')
```
Получение иерархии комментариев по ID родительского комментария:
```python
url = reverse('child', kwargs={"pk": pk})
response = client.get(url, format='json')
```
Удаление комментария по идентификатору:
```python
url = reverse('comment-item', kwargs={"pk": pk})
response = self.client.delete(url, format='json')
```
В случае, если комментарий имеет вложенные комментарии в response будет статус 400 и сообщение с просьбой удалить вложенные комментарии.






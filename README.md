# **Foodgran Project**

### Foodgram - веб-сервис, позволяющий пользователям интернета публиковать свои рецепты

<br/>

### Адрес сайта: **foodgramch1k.ddns.net / 89.104.66.15**

<br/>

### **Программный стэк:**
- Python
- Django Rest Framework
- Django ORM
- PostgreSQL
- Docker
- Postman

<br/>

### **Функционал приложения:**
- Регистрация и аутентификация пользователя
- Создание и изменение рецептов
- Добавление рецептов в избранное
- Добавление рецептов в корзину и скачивание файла с ингредиентами
- Доступ к API ресурса
- Доступ к админке ресурса

<br/>

### **Некоторые эндпоинты API:**
- Список ингредиентов: [GET /api/ingredients/](http://127.0.0.1/api/ingredients/)

- Получение ингредиента: [GET /api/ingredients/{id}/](http://127.0.0.1/api/ingredients/{id}/)

- Cписок тегов: [GET /api/tags/](http://127.0.0.1/api/tags/)

- Получение тега: [GET /api/tags/{id}/](http://127.0.0.1/api/tags/{id}/)

<br/>

### **Пример запроса к API:**
Создание рецепта: [POST /api/recipes/](http://127.0.0.1/api/recipes/)
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

<br/>

### **План развёртывания проектаа на сервере:**

Клонируем репозиторий:
```
git clone git@github.com:mrForza/foodgram-project-react.git
```

Переходим в папку:
```
cd foodgram-project-react/infra/
```

Запускаем контейнеры:
```
docker compose up
```

Выполняем миграции:
```
docker-compose exec backend python manage.py makemigrations

docker-compose exec backend python manage.py migrate
```

Собираем статику:
```
docker-compose exec backend python manage.py collectstatic
```

<br/>

# Доступ к админке:
login: admin@bk.ru
password: admin

<br/>

### Автор: **Громов Роман**
### Ссылка на github: **https://github.com/mrForza**

MAX_TEXTFIELD_LENGTH = 1024

MAX_CHARFIELD_LENGTH = 200

MAX_COLORFIELD_LENGTH = 7

MAX_COOKING_TIME = 1024

MIN_COOKING_TIME = 1

MAX_AMOUNT_OF_PRODUCTS = 100

MIN_AMOUNT_OF_PRODUCTS = 1

HELP_TEXT = {
    'tag_color': 'Цвет тэга',
    'tag_slug': 'Уникальный идентификатор тэга',
    'measurement_unit': 'Единица измерения ингредиента'
}

MIN_COOKING_TIME_ERROR = (f'Время приготовления блюда не может быть меньше '
                          f'{MIN_COOKING_TIME} минуты')

MAX_COOKING_TIME_ERROR = (f'Время приготовления блюда не может быть меньше '
                          f'{MAX_COOKING_TIME} минут')

MIN_AMOUNT_ERROR = (f'Количество ингредиентов не может быть меньше '
                    f'{MIN_AMOUNT_OF_PRODUCTS}')

MAX_AMOUNT_ERROR = (f'Количество ингредиентов не может быть больше '
                    f'{MAX_AMOUNT_OF_PRODUCTS} минут')

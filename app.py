import pandas as pd
import re
from datetime import datetime
import requests

# Чтение данных из CSV
df = pd.read_csv('data.csv')
columns = df.columns.tolist()


class Validator:
    def __init__(self, info_dict):
        self.info_dict = info_dict
        self.errors = {}
        self.dict_full_info_address = {}

    def print_errors(self):
        '''Возврат словаря ошибок'''
        return self.errors

    def first_name_space(self):
        '''Проверка пробелов в имени'''
        try:
            if ' ' in self.info_dict['b_crm_contact__first_name']:
                self.errors[self.info_dict['index']] += ['first_name_space_error']
        except KeyError:
            if ' ' in self.info_dict['b_crm_contact__first_name']:
                self.errors[self.info_dict['index']] = ['first_name_space_error']

    def last_name_space(self):
        '''Проверка пробелов в фамилии'''
        try:
            if ' ' in self.info_dict['b_crm_contact__LAST_NAME']:
                self.errors[self.info_dict['index']] += ['last_name_space_error']
        except KeyError:
            if ' ' in self.info_dict['b_crm_contact__LAST_NAME']:
                self.errors[self.info_dict['index']] = ['last_name_space_error']

    def patronymic_space(self):
        '''Проверка пробелов в отчестве'''
        try:
            if ' ' in self.info_dict['b_crm_contact__patronymic']:
                self.errors[self.info_dict['index']] += ['patronymic_space_error']
        except KeyError:
            if ' ' in self.info_dict['b_crm_contact__patronymic']:
                self.errors[self.info_dict['index']] = ['patronymic_space_error']

    def date_format(self):
        '''Проверка формата даты ГГГГ-ММ-ДД'''
        try:
            if re.search(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$',
                         self.info_dict['b_crm_contact__bdate']) is None:
                self.errors[self.info_dict['index']] += ['date_format_error']
        except KeyError:
            if re.search(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$',
                         self.info_dict['b_crm_contact__bdate']) is None:
                self.errors[self.info_dict['index']] = ['date_format_error']

    def departament_code(self):
        '''Проверка формата кода подразделения 111-111'''
        try:
            if re.search(r'^\d{3}-\d{3}$', self.info_dict['b_crm_contact__code']) is None:
                self.errors[self.info_dict['index']] += ['departament_code_error']
        except KeyError:
            if re.search(r'^\d{3}-\d{3}$', self.info_dict['b_crm_contact__code']) is None:
                self.errors[self.info_dict['index']] = ['departament_code_error']

    def passport_number_series(self):
        '''Проверка формата паспорта 0000 000000, три цифры подряд не могут повторяться;
        между номером и серией пробел'''
        try:
            if re.search(r'^(?!.*(\d)\1{3})\d{4} (?!.*(\d)\2{3})\d{6}(?!.*(\d)\3{3})$',
                         self.info_dict['b_crm_contact__series_and_number']) is None:
                self.errors[self.info_dict['index']] += ['passport_error']
        except KeyError:
            if re.search(r'^(?!.*(\d)\1{3})\d{4} (?!.*(\d)\2{3})\d{6}(?!.*(\d)\3{3})$',
                         self.info_dict['b_crm_contact__series_and_number']) is None:
                self.errors[self.info_dict['index']] = ['passport_error']

    def departament(self):
        '''Проверка названия департамента
        если меньше 10 символов или если
        меньше 3х слов
        между словами пробелы
        '''
        list_words = self.info_dict['b_crm_contact__department'].split(' ')
        try:
            if len(self.info_dict['b_crm_contact__department']) <= 10 or len(list_words) < 3:
                self.errors[self.info_dict['index']] += ['departament_error']
        except KeyError:
            if len(self.info_dict['b_crm_contact__department']) <= 10 or len(list_words) < 3:
                self.errors[self.info_dict['index']] = ['departament_error']

    def correct_date_of_issue(self):
        '''корректна ли дата выдачи относительно 14 лет'''
        birthdate = datetime.strptime(self.info_dict['b_crm_contact__bdate'], '%Y-%m-%d')
        date_issue = datetime.strptime(self.info_dict['b_crm_contact__date_of_issue'], '%Y-%m-%d')
        age = date_issue.year - birthdate.year
        try:
            if age > 14:
                pass
            # Проверяем, если человеку исполнилось ровно 14 лет
            elif age == 14:
                # Проверяем, что у человека день рождения уже прошел в этом году
                if (date_issue.month, date_issue.day) < (birthdate.month, birthdate.day):
                    self.errors[self.info_dict['index']] += ['correct_date_of_issue_error']
            else:
                self.errors[self.info_dict['index']] += ['correct_date_of_issue_error']
        except KeyError:
            if age > 14:
                pass
            # Проверяем, если человеку исполнилось ровно 14 лет
            elif age == 14:
                # Проверяем, что у человека день рождения уже прошел в этом году
                if (date_issue.month, date_issue.day) < (birthdate.month, birthdate.day):
                    self.errors[self.info_dict['index']] = ['correct_date_of_issue_error']
            else:
                self.errors[self.info_dict['index']] = ['correct_date_of_issue_error']

    def birthplace(self):
        '''Проверка на короткую строку места рождения
        если меньше 10 символов
        или если меньше 3х слов'''
        list_words = self.info_dict['b_crm_contact__birthplace'].split(' ')
        try:
            if len(self.info_dict['b_crm_contact__birthplace']) <= 10 or len(list_words) < 3:
                self.errors[self.info_dict['index']] += ['birthplace_error']
        except KeyError:
            if len(self.info_dict['b_crm_contact__birthplace']) <= 10 or len(list_words) < 3:
                self.errors[self.info_dict['index']] = ['birthplace_error']

    def registration_address(self):
        '''проверка на адрес регистрации если меньше 10 символов или меньше 3х слов
        проверяю до сиволов - |;|   '''
        main_string = self.info_dict['b_crm_contact__registration_address']
        list_main_string = main_string.split('|;|')
        first_string_list = list_main_string[0].split(' ')
        tracked_string = ' '.join(first_string_list)
        try:
            if len(tracked_string) <= 10 or len(first_string_list) < 3:
                self.errors[self.info_dict['index']] += ['registration_address_error']
        except KeyError:
            if len(tracked_string) <= 10 or len(first_string_list) < 3:
                self.errors[self.info_dict['index']] = ['registration_address_error']

    def full_info_address(self):
        '''полная информация из яндекс карт об адресе'''
        API_KEY = '4e4ca1e6-daf3-494a-9c97-f9f802887033'

        # Пример строки с адресом
        address_string = self.info_dict['b_crm_contact__registration_address']

        # URL для геокодирования
        geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address_string}&format=json"

        # Отправка запроса к API Яндекс.Карт
        response = requests.get(geocode_url)

        # Проверка статуса ответа
        if response.status_code == 200:
            result = response.json()

            # Извлечение данных из ответа
            if result['response']['GeoObjectCollection']['featureMember']:
                geo_object = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

                # Получение полной строки адреса
                full_address = geo_object['metaDataProperty']['GeocoderMetaData']['text']
                self.dict_full_info_address['full_address'] = full_address

                # Извлечение компонентов адреса
                address_components = geo_object['metaDataProperty']['GeocoderMetaData']['Address']['Components']
                for component in address_components:
                    self.dict_full_info_address[f"{component['kind']}"] = f"{component['name']}"
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
        return self.dict_full_info_address


def dev_dict(index, seria):
    '''Создает словарь из одной записи: колонка -> значение колонки'''
    _dict = {'index': index}
    for col in columns:
        _dict[col] = seria[col]
    return _dict


content = {
    'index': 0,
    'Unnamed: 0': 0,
    'nindex': 90286,
    'b_crm_contact__first_name': 'Наталья',
    'b_crm_contact__LAST_NAME': 'Кононенко',
    'b_crm_contact__patronymic': 'Матвеевна',
    'b_crm_contact__bdate': '1990-09-23',
    'b_crm_contact__gender': 'жен',
    'b_crm_contact__code': '012-321',
    'b_crm_contact__series_and_number': '3212 8361745',
    'b_crm_contact__department': 'МВД по Республике Адыгея',
    'b_crm_contact__date_of_issue': '2021-06-18',
    'b_crm_contact__birthplace': 'Россия',
    'b_crm_contact__registration_address': 'республика Адыгея ,г. Майкоп ,ул. 12 Марта ,13...'
}
# проверка на введенный нами словарь 'content' с нашими данными
try:
    all_errors_content = []
    for i in range(1):
        obj = Validator(content)
        print('\nПРОВЕРЯЕМ ВВЕДЕННЫЙ СЛОВАРЬ\n')
        # Применяем все методы к объекту
        for attr_name in dir(obj):
            attr = getattr(obj, attr_name)
            if callable(attr) and attr_name not in dir(Validator.__base__):
                try:
                    attr()
                except TypeError:
                    print(f"{attr_name} требует аргументы, пропускаем его")

        if obj.print_errors():
            all_errors_content.append(obj.print_errors())
        print(i, ':', obj.dict_full_info_address, '\n')
    print(f'Ошибки введенного словаря:\n{all_errors_content}')
    print('\nДАЛЬШЕ ПРОВЕРКА DATAFRAME\n')
except BaseException:
    pass

# Проходимся по всему DataFrame и создаем словари по каждой записи
all_errors = []
for i in range(len(df)):
    seria = df.iloc[i]
    obj = Validator(dev_dict(i, seria))
    # Применяем все методы к объекту
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if callable(attr) and attr_name not in dir(Validator.__base__):
            try:
                attr()
            except TypeError:
                print(f"{attr_name} требует аргументы, пропускаем его")

    if obj.print_errors():
        all_errors.append(obj.print_errors())
    print(i, ':', obj.dict_full_info_address, '\n')

# Вывод ошибок
for error in all_errors:
    print(error)

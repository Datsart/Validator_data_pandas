import pandas as pd
import re
from datetime import datetime
import requests
import inspect

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

    def add_error(self, error_type):
        '''Добавление ошибки в словарь'''
        if self.info_dict['index'] not in self.errors:
            self.errors[self.info_dict['index']] = []
        self.errors[self.info_dict['index']].append(error_type)

    def first_name_space(self):
        '''Проверка пробелов в имени и только кириллица'''
        if ' ' in self.info_dict['b_crm_contact__first_name'] or re.search(r'^[а-яА-ЯёЁ]+$', self.info_dict[
            'b_crm_contact__first_name']) is None:
            self.add_error('first_name_space_error')

    def last_name_space(self):
        '''Проверка пробелов в фамилии и только кириллица'''
        if ' ' in self.info_dict['b_crm_contact__LAST_NAME'] or re.search(r'^[а-яА-ЯёЁ]+$', self.info_dict[
            'b_crm_contact__LAST_NAME']) is None:
            self.add_error('last_name_space_error')

    def patronymic_space(self):
        '''Проверка пробелов в отчестве и только кириллица'''
        if ' ' in self.info_dict['b_crm_contact__patronymic'] or re.search(r'^[а-яА-ЯёЁ]+$', self.info_dict[
            'b_crm_contact__patronymic']) is None:
            self.add_error('patronymic_space_error')

    def birtday_date_format(self):
        '''Проверка формата даты ГГГГ-ММ-ДД;
        проверка на возраст 14 лет'''
        try:
            date = datetime.strptime(self.info_dict['b_crm_contact__bdate'], '%Y-%m-%d')
            today = datetime.today()
            age = today.year - date.year - ((today.month, today.day) < (date.month, date.day))

            if age < 14:
                self.add_error('birtday_date_format')
        except Exception:
            self.add_error('birtday_date_format')

    def departament_code(self):
        '''Проверка формата кода подразделения 111-111'''
        if re.search(r'^\d{3}-\d{3}$', self.info_dict['b_crm_contact__code']) is None:
            self.add_error('departament_code_error')

    def passport_number_series(self):
        '''Проверка формата паспорта 0000 000000;
        в серии 3 цифры подряд идти не могут в номере 3 цифры подряд идти не могут;
        между номером и серией пробел'''
        if re.search(r'^(?!.*(\d)\1\1)\d{4} (?!.*(\d)\2\2\2)\d{6}$',
                     self.info_dict['b_crm_contact__series_and_number']) is None:
            self.add_error('passport_error')

    def departament(self):
        '''Проверка названия департамента если меньше 10 символов или если меньше 3х слов
        между словами пробелы;
        если строка начинается или заканчивается пробелом;
        могут быть пробелы точки тире и кириллица'''
        list_words = self.info_dict['b_crm_contact__department'].split(' ')
        if len(self.info_dict['b_crm_contact__department']) <= 10 or len(list_words) < 3:
            self.add_error('departament_error')
        elif self.info_dict['b_crm_contact__department'].startswith(' ') or self.info_dict[
            'b_crm_contact__department'].endswith(' '):
            self.add_error('departament_error')
        elif re.search(r'^[А-Яа-яЁё0-9\s\.\-]+$', self.info_dict['b_crm_contact__department']) is None:
            self.add_error('departament_error')

    def correct_date_of_issue(self):
        '''Корректна ли дата выдачи относительно 14 лет;
        корректность формата даты'''
        try:
            birthdate = datetime.strptime(self.info_dict['b_crm_contact__bdate'], '%Y-%m-%d')
            date_issue = datetime.strptime(self.info_dict['b_crm_contact__date_of_issue'], '%Y-%m-%d')
            age = date_issue.year - birthdate.year
            if age < 14 or (age == 14 and (date_issue.month, date_issue.day) < (birthdate.month, birthdate.day)):
                self.add_error('correct_date_of_issue_error')
        except BaseException:
            self.add_error('correct_date_of_issue_error')

    def birthplace(self):
        '''Проверка на короткую строку места рождения если меньше 10 символов или если меньше 3х слов;
        проверка на пробел до или после строки;
        может быть только кириллица пробелы точки и тире'''
        list_words = self.info_dict['b_crm_contact__birthplace'].split(' ')
        if len(self.info_dict['b_crm_contact__birthplace']) <= 10 or len(list_words) < 3:
            self.add_error('birthplace_error')
        elif self.info_dict['b_crm_contact__birthplace'].startswith(
                ' ') or self.info_dict['b_crm_contact__birthplace'].endswith(' '):
            self.add_error('birthplace_error')
        elif re.search(r'^[А-Яа-яЁё0-9\s\.\-]+$', self.info_dict['b_crm_contact__birthplace']) is None:
            self.add_error('birthplace_error')

    def registration_address(self):
        '''Проверка на адрес регистрации если меньше 10 символов или меньше 3х слов проверяю до символов - |;|'''
        main_string = self.info_dict['b_crm_contact__registration_address']
        list_main_string = main_string.split('|;|')
        first_string_list = list_main_string[0].split(' ')
        tracked_string = ' '.join(first_string_list)
        if len(tracked_string) <= 10 or len(first_string_list) < 3:
            self.add_error('registration_address_error')
        elif main_string.startswith(' ') or main_string.endswith(' '):
            self.add_error('registration_address_error')

    def full_info_address(self):
        '''Полная информация из Яндекс.Карт об адресе'''
        API_KEY = '4e4ca1e6-daf3-494a-9c97-f9f802887033'
        address_string = self.info_dict['b_crm_contact__registration_address']
        geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address_string}&format=json"
        response = requests.get(geocode_url)
        if response.status_code == 200:
            result = response.json()
            if result['response']['GeoObjectCollection']['featureMember']:
                geo_object = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                full_address = geo_object['metaDataProperty']['GeocoderMetaData']['text']
                self.dict_full_info_address['full_address'] = full_address
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
    'b_crm_contact__bdate': '2010-09-22',
    'b_crm_contact__gender': 'жен',
    'b_crm_contact__code': '012-321',
    'b_crm_contact__series_and_number': '3212 837745',
    'b_crm_contact__department': 'МВД по Республике Адыгея',
    'b_crm_contact__date_of_issue': '2024-09-21',
    'b_crm_contact__birthplace': 'Россия',
    'b_crm_contact__registration_address': 'республика Адыгея ,г. Майкоп ,ул. 12 Марта ,13...'
}

try:
    all_errors_content = []
    for i in range(1):
        obj = Validator(content)
        print('\nПРОВЕРЯЕМ ВВЕДЕННЫЙ СЛОВАРЬ\n')
        for attr_name in dir(obj):
            attr = getattr(obj, attr_name)
            if callable(attr) and attr_name not in dir(Validator.__base__):
                if not inspect.signature(attr).parameters:
                    try:
                        attr()
                    except TypeError:
                        print(f"{attr_name} требует аргументы, пропускаем его")
        if obj.print_errors():
            all_errors_content.append(obj.print_errors())
        print(i, ':', obj.dict_full_info_address, '\n')
    print(f'Ошибки введенного словаря:\n{all_errors_content}')
    print('\nДАЛЬШЕ ПРОВЕРКА DATAFRAME\n')
except BaseException as e:
    print(e)

# Проходимся по всему DataFrame и создаем словари по каждой записи
all_errors = []
for i in range(len(df)):
    seria = df.iloc[i]
    obj = Validator(dev_dict(i, seria))
    # Применяем все методы к объекту
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if callable(attr) and attr_name not in dir(Validator.__base__):
            if not inspect.signature(attr).parameters:
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

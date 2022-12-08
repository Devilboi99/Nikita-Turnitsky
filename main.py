import csv
import datetime
import re
import sys

from prettytable import PrettyTable


def main():
    convert = ConvertCsvToTable()
    convert.MakeConvert()
    convert.PrintTable()


class Salary:
    """класс работает в данными зарплаты.

    Attributes:
         From (int) - нижняя граница вклада
         To (int) - Верхняя граница вклада
         Gross (Str) - с налогом или нет
         Currency (int) - валюта
    """
    CurrencyToRub = {
        "Манаты": 35.68,
        "Белорусские рубли": 23.91,
        "Евро": 59.90,
        "Грузинский лари": 21.74,
        "Киргизский сом": 0.76,
        "Тенге": 0.13,
        "Рубли": 1,
        "Гривны": 1.64,
        "Доллары": 60.66,
        "Узбекский сум": 0.0055,
    }

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.From = salary_from
        self.To = salary_to
        self.Gross = salary_gross
        self.Currency = salary_currency

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return f"{Formate.ToNum(self.From)} - {Formate.ToNum(self.To)} ({self.Currency}) ({self.Gross})"

    def ArithmeticalMean(self):
        """ выдаёт среднее значение от верхней и нижней границы
        """
        return (self.From * self.CurrencyToRub[self.Currency] + self.To * self.CurrencyToRub[self.Currency]) / 2


class TableConfig:
    """ Класс для настройки таблицы:

         Attributes:
             FileName (str) - название файла откуда будут брать данные для таблицы
             FilterValues (str) - какие данные будут фильтроваться
             SortValues (str) - что будет сортироваться
             IsRecerse (bool) - таблица риверсированая
             Range (str) - как диапазон данных из таблицы вывести
             FilterAttribures (str) - какие атрибуты будут выводиться

    """

    def __init__(self):
        self.__FileName = input("Введите название файла: ")
        self.FilterValues = input("Введите параметр фильтрации: ")
        self.SortValue = input("Введите параметр сортировки: ")
        self.IsReverse = input("Обратный порядок сортировки (Да / Нет): ")
        self.Range = input("Введите диапазон вывода: ")
        self.FilterAttributes = input("Введите требуемые столбцы: ")

    @property
    def FileData(self):
        return self.__FileData

    def CheckSortInput(self, attributes):
        """проверка есть ли такой атрибут в таблицы ну и корректность данных"""
        if not (self.SortValue in attributes or self.SortValue == ""):
            print("Параметр сортировки некорректен")
            sys.exit()
        if not (self.IsReverse == "Да" or self.IsReverse == "Нет" or self.IsReverse == ""):
            print("Порядок сортировки задан некорректно")
            sys.exit()

    def SetConfig(self):
        """идет полная настройка конфигураций таблицы : перед использование нужно это сделать"""
        self.__TakeFile(self.__FileName)
        if len(self.FilterValues) != 0:
            self.__ConfigurateFilterRows(self.FilterValues)
        self.__ConfigurateFilterAttributes(self.FilterAttributes)
        self.Range = self.Range.split(' ')

    def __ConfigurateFilterRows(self, filterValues):
        """настройка фильтра по значению"""
        if ':' in filterValues:
            result = filterValues.split(': ')
            if len(result) > 1:
                self.FilterValues = result
        else:
            print("Формат ввода некорректен")
            sys.exit()

    def __TakeFile(self, fileName):
        """берем файл с пк с данными"""
        File = open(fileName, encoding='utf_8_sig')  # vacancies_medium.csv 20 30 Название, Опыт работы, Оклад
        self.__FileData = [row for row in csv.reader(File)]
        if len(self.FileData) == 0:
            print("Пустой файл")
            sys.exit()

    def __ConfigurateFilterAttributes(self, filterAttributes):
        """настройка фильтра атрибутов"""
        self.FilterAttributes = [column for column in filterAttributes.split(', ')]
        self.FilterAttributes.append('№')

    def GetFilteredRow(self, personsInfo):  # плз когда нибудь перепеши это чудо в лямды
        """получаем отфильтрованную таблицу с нужными нам данными"""
        personsInfoWithFilter = []
        for personInfo in personsInfo:
            if self.FilterValues[0] not in personInfo.keys() and self.FilterValues[0] != 'Идентификатор валюты оклада':
                print("Параметр поиска некорректен")
                sys.exit()
            if self.FilterValues[0] == 'Навыки':
                count = 0
                skillsFind = self.FilterValues[1].split(', ')
                for i in skillsFind:
                    for e in personInfo['Навыки']:
                        if i == e:
                            count += 1
                if count == len(skillsFind):
                    personsInfoWithFilter.append(personInfo)
            elif self.FilterValues[0] == 'Оклад':
                salaries = personInfo['Оклад']
                if salaries.From <= int(self.FilterValues[1]) <= salaries.To:
                    personsInfoWithFilter.append(personInfo)
            elif self.FilterValues[0] == 'Идентификатор валюты оклада':
                if personInfo['Оклад'].Currency == self.FilterValues[1]:
                    personsInfoWithFilter.append(personInfo)
            else:
                if self.FilterValues[1] == personInfo[self.FilterValues[0]]:
                    personsInfoWithFilter.append(personInfo)

        if len(personsInfoWithFilter) == 0:
            print("Ничего не найдено")
            sys.exit()

        return personsInfoWithFilter


class TableData:
    """Данные таблицы: атрибуты и значения

        Attributes:
            Attributes (list) - атрибуты
            Rows (list) - значения атрибутов
    """
    def __init__(self, attributes, rows):
        self.Attributes = attributes
        self.Rows = rows


class ConvertCsvToTable:
    """
        класс/программа для конвертаций csv файла в таблицу prettytable

        Attributes:
            __Table (prettyTable) - будущая таблица
            __TableConfig (TableConfig) - настройки к таблицы
            __CountRow (int) - количества строк

    """
    def __init__(self):
        self.__Table = PrettyTable()
        self.__TableConfig = TableConfig()
        self.__CountRow = 1

    def MakeConvert(self):
        """Занимается конвентированием данных из csv в table и настройкой таблицы"""
        self.__TableConfig.SetConfig()
        tableData = self.__GetTableData()

        self.__TableConfigurateAndSetAttributes(tableData.Attributes)

        if len(self.__TableConfig.FilterValues) != 0:
            tableData.Rows = self.__TableConfig.GetFilteredRow(tableData.Rows)

        self.__TableConfig.CheckSortInput(tableData.Attributes)

        dictfunc = self.__CreateFuncSort()
        if self.__TableConfig.SortValue != '':
            tableData.Rows.sort(key=dictfunc[self.__TableConfig.SortValue],
                                reverse=(self.__TableConfig.IsReverse == 'Да'))

        self.__SetTable(tableData.Rows)

    def __CreateFuncSort(self):
        """лямдя для работы с сортировокой"""
        return {"Оклад": lambda row: row["Оклад"].ArithmeticalMean(),
                "Название": lambda row: row["Название"],
                "Компания": lambda row: row["Компания"],
                "Навыки": lambda row: len(row["Навыки"]) if type(row["Навыки"]).__name__ == 'list' else 1,
                "Опыт работы": lambda row: int(row["Опыт работы"].split(" ")[1]) if len(
                    row["Опыт работы"].split(" ")[1]) == 1 else 0,
                "Название региона": lambda row: row["Название региона"],
                "Дата публикации вакансии": lambda row: row["Дата публикации вакансии"]}

    def __TableConfigurateAndSetAttributes(self, attributes):
        """настраивает prettyTable и ставить атрибуты"""
        self.__Table.field_names = ["№"] + attributes
        self.__Table._max_width = {el: 20 for el in self.__Table.field_names}
        self.__Table.align = "l"
        self.__Table.hrules = True
        self.__Table

    def __GetTableData(self):
        """получение данных в формате для чтения"""
        personsInfo = []
        translateEngRu = GetTranslateEngRu()
        attributes = self.__TableConfig.FileData.pop(0)
        attributesInRu = [translateEngRu[attribute] for attribute in attributes]
        for row in self.__TableConfig.FileData:
            if self.__RowIsFull(len(attributes), row):
                convertRow = TryTranslate(self.__CsvFilter(row), translateEngRu)
                personsInfo.append(self.__CreateDict(attributesInRu, convertRow))

        if len(personsInfo) == 0:
            print("Нет данных")
            sys.exit()

        return TableData(list(personsInfo[0].keys()), personsInfo)

    def __CreateDict(self, nameColumn, row):
        """создает словарь атрибут - значение"""
        dict = {}
        isFirst = True
        for i in range(0, len(row)):
            if self.IsSalary(nameColumn[i]) and isFirst:
                isFirst = False
                dict['Оклад'] = self.MergeSalary(row, i)
            elif nameColumn[i] == 'Дата и время публикации вакансии':
                dict['Дата публикации вакансии'] = datetime.datetime.strptime(row[i], "%Y-%m-%dT%H:%M:%S%z").strftime(
                    "%d.%m.%Y")
            elif not self.IsSalary(nameColumn[i]):
                dict[nameColumn[i]] = row[i]
        return dict

    def __SetTable(self, personsInfo):
        """добавляет значения в prettyTable"""
        for rowPersonInfo in personsInfo:
            total = []
            for attributeInfo in rowPersonInfo.values():
                if type(attributeInfo).__name__ == 'list':
                    attributeInfo = '\n'.join(attributeInfo)
                total.append(CheckLen(attributeInfo))
            self.__Table.add_row([self.__CountRow] + [e for e in total])
            self.__CountRow += 1

    def PrintTable(self):
        """рисует таблицу"""
        rangeStart = int(self.__TableConfig.Range[0]) - 1 if self.__TableConfig.Range[0] != '' else 0
        rangeFinish = int(self.__TableConfig.Range[1]) - 1 if len(self.__TableConfig.Range) == 2 else self.__CountRow
        all_columns = self.__TableConfig.FilterAttributes if len(
            self.__TableConfig.FilterAttributes) != 2 else self.__Table.field_names
        print(self.__Table.get_string(start=rangeStart, end=rangeFinish, fields=all_columns))

    @staticmethod
    def __RowIsFull(lenLine, row):
        """проверяет все ли значение на месте"""
        if lenLine != len(row):
            return False
        for e in row:
            if e == '':
                return False
        return True

    @staticmethod
    def __CsvFilter(row):
        """убирает мусор из данных Csv"""
        rowWithoutHtml = []
        for line in row:
            if line.find("\n") != -1:
                rowWithoutHtml.append([Formate.clearStr(el) for el in line.split('\n')])
            else:
                rowWithoutHtml.append(Formate.clearStr(line))
        return rowWithoutHtml

    @staticmethod
    def IsSalary(line):
        """проверят это зарплата ли"""
        return line == 'Нижняя граница вилки оклада' or line == 'Верхняя граница вилки оклада' or line == 'Оклад указан до вычета налогов' or line == 'Идентификатор валюты оклада'

    @staticmethod
    def MergeSalary(row, i):
        """соеденяет все данные связанные с зарплатой"""
        list = []
        dict = {'Да': 'Без вычета налогов', 'Нет': 'С вычетом налогов'}
        for j in range(0, 3):
            list.append(row[j + i])
        salary = Salary(int(float(list[0])), int(float(list[1])), list[2])
        return salary


class Formate:
    """дополнительные методы связанные с изменением формата данных"""
    @staticmethod
    def clearStr(StrValue):
        """"чистит от html кода данные"""
        return ' '.join(re.sub(r"<[^>]+>", '', StrValue).split())

    @staticmethod
    def ToNum(line):
        """ преврашет значение в число
        """
        out = ''
        line = str(line)
        prevPlace = 0
        gap = len(line) % 3
        while gap < len(line):
            out += line[prevPlace:gap] + ' '
            prevPlace = gap
            gap += 3
        out += line[prevPlace:gap]
        return out.strip()


def GetTranslateEngRu():
    """словарь с переводм слов"""
    return {'name': 'Название',
            'description': 'Описание',
            'key_skills': 'Навыки',
            'experience_id': 'Опыт работы',
            'premium': 'Премиум-вакансия',
            'employer_name': 'Компания',
            'salary_from': 'Нижняя граница вилки оклада',
            'salary_to': 'Верхняя граница вилки оклада',
            'salary_gross': 'Оклад указан до вычета налогов',
            'salary_currency': 'Идентификатор валюты оклада',
            'area_name': 'Название региона',
            'published_at': 'Дата и время публикации вакансии',
            'True': 'Да',
            'False': 'Нет',
            "noExperience": "Нет опыта",
            "between1And3": "От 1 года до 3 лет",
            "between3And6": "От 3 до 6 лет",
            "moreThan6": "Более 6 лет",
            "AZN": "Манаты",
            "BYR": "Белорусские рубли",
            "EUR": "Евро",
            "GEL": "Грузинский лари",
            "KGS": "Киргизский сом",
            "KZT": "Тенге",
            "RUR": "Рубли",
            "UAH": "Гривны",
            "USD": "Доллары",
            "UZS": "Узбекский сум",
            }


def TryTranslate(row, translateEngRu):
    """пытатся перевести значения"""
    for j in range(0, len(row)):
        if type(row[j]).__name__ == 'list':
            for line in row[j]:
                if tuple(line) in translateEngRu.keys():
                    row[j] = translateEngRu[line]  # код который ничего по факту не делает убрать!!
        else:
            if row[j] in translateEngRu.keys():
                row[j] = translateEngRu[row[j]]
    return row


def CheckLen(attributeInfo):
    """"проверяет длину значения атрибута"""
    if len(attributeInfo) > 100:
        return attributeInfo[:100] + "..."
    return attributeInfo


if __name__ == '__main__':
    main()

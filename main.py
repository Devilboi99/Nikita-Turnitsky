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
        return f"{Formate.Num(self.From)} - {Formate.Num(self.To)} ({self.Currency}) ({self.Gross})"

    def ArithmeticalMean(self):
        return (self.From * self.CurrencyToRub[self.Currency] + self.To * self.CurrencyToRub[self.Currency]) / 2


class TableConfig:
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
        if not (self.SortValue in attributes or self.SortValue == ""):
            print("Параметр сортировки некорректен")
            sys.exit()
        if not (self.IsReverse == "Да" or self.IsReverse == "Нет" or self.IsReverse == ""):
            print("Порядок сортировки задан некорректно")
            sys.exit()

    def SetConfig(self):
        self.__TakeFile(self.__FileName)
        if len(self.FilterValues) != 0:
            self.__ConfigurateFilterRows(self.FilterValues)
        self.__ConfigurateFilterAttributes(self.FilterAttributes)
        self.Range = self.Range.split(' ')

    def __ConfigurateFilterRows(self, filter):
        if ':' in filter:
            result = filter.split(': ')
            if len(result) > 1:
                self.FilterValues = result
        else:
            print("Формат ввода некорректен")
            sys.exit()

    def __TakeFile(self, fileName):
        File = open(fileName, encoding='utf_8_sig')  # vacancies_medium.csv 20 30 Название, Опыт работы, Оклад
        self.__FileData = [row for row in csv.reader(File)]
        if len(self.FileData) == 0:
            print("Пустой файл")
            sys.exit()

    def __ConfigurateFilterAttributes(self, filterAttributes):
        self.FilterAttributes = [column for column in filterAttributes.split(', ')]
        self.FilterAttributes.append('№')

    def GetFilteredRow(self, personsInfo):  # плз когда нибудь перепеши это чудо в лямды
        personsInfoWithFilter = []
        for personInfo in personsInfo:
            if self.FilterValues[0] not in personInfo.keys() and self.FilterValues[0] != 'Идентификатор валюты оклада':
                print("Параметр поиска некорректен")
                sys.exit()
            if self.FilterValues[0] == 'Навыки':
                count = 0
                skills = self.FilterValues[1].split(', ')
                for i in skills:
                    for e in personInfo['Навыки']:
                        if i == e:
                            count += 1
                if count == len(skills):
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
    def __init__(self, attributes, rows):
        self.Attributes = attributes
        self.Rows = rows


class ConvertCsvToTable:

    def __init__(self):
        self.__Table = PrettyTable()
        self.__TableConfig = TableConfig()
        self.__CountRow = 1

    def MakeConvert(self):
        self.__TableConfig.SetConfig()
        tableData = self.__GetTableData()

        self.TableConfigurateAndSetAttributes(tableData.Attributes)

        if len(self.__TableConfig.FilterValues) != 0:
            tableData.Rows = self.__TableConfig.GetFilteredRow(tableData.Rows)

        self.__TableConfig.CheckSortInput(tableData.Attributes)

        dictfunc = self.CreateFuncSort()
        if self.__TableConfig.SortValue != '':
            tableData.Rows.sort(key=dictfunc[self.__TableConfig.SortValue], reverse=(self.__TableConfig.IsReverse == 'Да'))

        self.__SetTable(tableData.Rows)

    def CreateFuncSort(self):
        return {"Оклад": lambda row: row["Оклад"].ArithmeticalMean(),
                "Название": lambda row: row["Название"],
                "Компания": lambda row: row["Компания"],
                "Навыки": lambda row: len(row["Навыки"]) if type(row["Навыки"]).__name__ == 'list' else 1,
                "Опыт работы": lambda row: int(row["Опыт работы"].split(" ")[1]) if len(row["Опыт работы"].split(" ")[1]) == 1 else 0,
                "Название региона": lambda row: row["Название региона"],
                "Дата публикации вакансии": lambda row: row["Дата публикации вакансии"]}

    def TableConfigurateAndSetAttributes(self, attributes):
        self.__Table.field_names = ["№"] + attributes
        self.__Table._max_width = {el: 20 for el in self.__Table.field_names}
        self.__Table.align = "l"
        self.__Table.hrules = True
        self.__Table

    def __GetTableData(self):
        personsInfo = []
        translateEngRu = GetTranslateEngRu()
        attributes = self.__TableConfig.FileData.pop(0)
        attributesInRu = [translateEngRu[attribute] for attribute in attributes]
        for row in self.__TableConfig.FileData:
            if RowIsFull(len(attributes), row):
                convertRow = TryTranslate(CsvFilter(row), translateEngRu)
                personsInfo.append(self.__CreateDict(attributesInRu, convertRow))

        if len(personsInfo) == 0:
            print("Нет данных")
            sys.exit()

        return TableData(list(personsInfo[0].keys()), personsInfo)

    @staticmethod
    def __CreateDict(nameColumn, row):
        dict = {}
        isFirst = True
        for i in range(0, len(row)):
            if IsSalary(nameColumn[i]) and isFirst:
                isFirst = False
                dict['Оклад'] = MergeSalary(row, i)
            elif nameColumn[i] == 'Дата и время публикации вакансии':
                dict['Дата публикации вакансии'] = datetime.datetime.strptime(row[i], "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y")
            elif not IsSalary(nameColumn[i]):
                dict[nameColumn[i]] = row[i]
        return dict

    def __SetTable(self, personsInfo):
        for rowPersonInfo in personsInfo:
            total = []
            for attributeInfo in rowPersonInfo.values():
                if type(attributeInfo).__name__ == 'list':
                    attributeInfo = '\n'.join(attributeInfo)
                total.append(CheckLen(attributeInfo))
            self.__Table.add_row([self.__CountRow] + [e for e in total])
            self.__CountRow += 1

    def PrintTable(self):
        rangeStart = int(self.__TableConfig.Range[0]) - 1 if self.__TableConfig.Range[0] != '' else 0
        rangeFinish = int(self.__TableConfig.Range[1]) - 1 if len(self.__TableConfig.Range) == 2 else self.__CountRow
        all_columns = self.__TableConfig.FilterAttributes if len(
            self.__TableConfig.FilterAttributes) != 2 else self.__Table.field_names
        print(self.__Table.get_string(start=rangeStart, end=rangeFinish, fields=all_columns))


class Formate:
    @staticmethod
    def clearStr(StrValue):
        return ' '.join(re.sub(r"<[^>]+>", '', StrValue).split())

    @staticmethod
    def Num(line):
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


def RowIsFull(lenLine, row):
    if lenLine != len(row):
        return False
    for e in row:
        if e == '':
            return False
    return True


def IsSalary(line):
    return line == 'Нижняя граница вилки оклада' or line == 'Верхняя граница вилки оклада' or line == 'Оклад указан до вычета налогов' or line == 'Идентификатор валюты оклада'


def MergeSalary(row, i):
    list = []
    dict = {'Да': 'Без вычета налогов', 'Нет': 'С вычетом налогов'}
    for j in range(0, 4):
        list.append(row[j + i])
    salary = Salary(int(float(list[0])), int(float(list[1])), dict[list[2]], list[3])
    return salary




def CsvFilter(row):
    rowWithoutHtml = []
    for line in row:
        if line.find("\n") != -1:
            rowWithoutHtml.append([Formate.clearStr(el) for el in line.split('\n')])
        else:
            rowWithoutHtml.append(Formate.clearStr(line))
    return rowWithoutHtml


def TryTranslate(row, translateEngRu):
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
    if len(attributeInfo) > 100:
        return attributeInfo[:100] + "..."
    return attributeInfo


if __name__ == '__main__':
    main()

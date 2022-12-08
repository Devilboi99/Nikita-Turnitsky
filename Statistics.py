import csv
import re
import sys
import datetime


def main():
    statisticsApp = StatisticsApp()
    nameFile = input('Введите название файла: ')
    profession = input('Введите название профессии: ')
    statisticsApp.LoadCsvFile(nameFile)
    statisticsApp.SetData()
    statisticsApp.LoadSettings(profession)
    statisticsApp.DataPreparation()
    statisticsApp.CreateCsvFileByYear()
    statisticsApp.PrintDynamicsSalaryVacancyByYear()
    statisticsApp.PrintDynamicsFilterVacancyByYear()
    statisticsApp.printDymabicsByCity()
    input('Press ENTER to exit')

class StatisticsApp:
    """"программа, преваращющая данные в статистику"""
    def __init__(self):
        self.__FileData = ''
        self.__Profession = ''
        self.__DynamicsSalaryByYear = {}
        self.__DynamicsSalaryByCity = {}
        self.__TotalVacancies = 0

    def DataPreparation(self):
        """подготавливает данные для вывода статистики"""
        vacancies = self.__GetVacancies()
        self.__TotalVacancies = len(vacancies)
        self.__SetStatistics(vacancies)

    def __SetStatistics(self, vacancies):
        """устанавливает данные по датам и городам"""
        for vacancy in vacancies:
            if not self.IsAdded(vacancy.publishedAt.year, self.__DynamicsSalaryByYear):
                self.__DynamicsSalaryByYear[vacancy.publishedAt.year] = []
            if not self.IsAdded(vacancy.areaName, self.__DynamicsSalaryByCity):  ## дублируется код убрать потом
                self.__DynamicsSalaryByCity[vacancy.areaName] = []
            self.__DynamicsSalaryByYear[vacancy.publishedAt.year].append(vacancy)
            self.__DynamicsSalaryByCity[vacancy.areaName].append(vacancy)

    @staticmethod
    def IsAdded(element, dynamics):
        """проверяет добавлен ли ключ"""
        return element in dynamics.keys()

    def PrintDynamicsSalaryVacancyByYear(self):
        """выводит данные по годам"""
        print("Динамика уровня зарплат по годам: " + str(
            {k: self.GetAverageSalary(v) for k, v in self.__DynamicsSalaryByYear.items()}))
        print("Динамика количества вакансий по годам: " + str(
            {k: int(len(v)) for k, v in self.__DynamicsSalaryByYear.items()}))

    def PrintDynamicsFilterVacancyByYear(self):
        """выводит данные по годам с учётом профессий"""
        print("Динамика уровня зарплат по годам для выбранной профессии: " + str(
            {k: self.GetAverageSalary(list(filter(lambda x: self.__Profession in x.name, v))) for k, v in
             self.__DynamicsSalaryByYear.items()}))

        print("Динамика количества вакансий по годам для выбранной профессии: " + str(
            {k: int(len(list(filter(lambda x: self.__Profession in x.name, v)))) for k, v in
             self.__DynamicsSalaryByYear.items()}))

    def printDymabicsByCity(self):
        """выводит данные по городам"""
        result = {k: self.GetAverageSalary(v) for k, v in self.__DynamicsSalaryByCity.items() if
                  round(len(v) / self.__TotalVacancies, 4) >= 0.01}
        print("Уровень зарплат по городам (в порядке убывания): " + str(
            dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])))

        result = {k: round(len(v) / self.__TotalVacancies, 4) for k, v in self.__DynamicsSalaryByCity.items() if
                  round(len(v) / self.__TotalVacancies, 4) >= 0.01}
        print("Доля вакансий по городам (в порядке убывания): " + str(
            dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])))

    def LoadCsvFile(self, fileName):
        File = open(fileName, encoding='utf_8_sig')
        self.__FileData = [row for row in csv.reader(File)]
        if len(self.__FileData) == 0:
            print("Пустой файл")  ## кринж
            sys.exit()

    def LoadSettings(self, profession):
        self.__Profession = profession

    def __GetVacancies(self):
        """превращает данные в стукрутру vacancy"""
        personsInfo = []
        for row in self.__FileData:
            personsInfo.append(Vacancy(row))

        if len(personsInfo) == 0:
            print("Нет данных")  ## пж напиши здесь tru catch умоляю, это не смешно плзззз
            sys.exit()

        return personsInfo

    @staticmethod
    def GetAverageSalary(vacancies):
        """выводит среднию зарплату по вакансиям"""
        salaryAverage = 0
        if len(vacancies) == 0:
            return 0
        for vacancy in vacancies:
            salaryAverage += vacancy.Salary.ArithmeticalMean()

        return int(salaryAverage // len(vacancies))

    @staticmethod
    def __RowIsFull(lenLine, row):
        """проверяет все ли значение на месте"""
        if lenLine != len(row):
            return False
        for e in row:
            if e == '':
                return False
        return True

    def SetData(self):
        """получение данных в формате для чтения"""
        if len(self.__FileData) == 6:
            return
        personsInfo = []
        attributes = self.__FileData.pop(0)
        for row in self.__FileData:
            if self.__RowIsFull(len(attributes), row):
                personsInfo.append(self.__CreateDict(attributes, self.__CsvFilter(row)))
        if len(personsInfo) == 0:
            print("Нет данных")
            sys.exit()
        info = []
        for person in personsInfo:
            info.append([person['name'],
                         person['salary_from'],
                         person['salary_to'], person['salary_currency'], person['area_name'], person['published_at']])

        self.__FileData = info

    @staticmethod
    def __CreateDict(nameColumn, row):
        dict = {}
        for i in range(0, len(row)):
            dict[nameColumn[i]] = row[i]
        return dict

    def __CsvFilter(self, row):
        """убирает мусор из данных Csv"""
        rowWithoutHtml = []
        for line in row:
            if line.find("\n") != -1:
                rowWithoutHtml.append([self.clearStr(el) for el in line.split('\n')])
            else:
                rowWithoutHtml.append(self.clearStr(line))
        return rowWithoutHtml

    @staticmethod
    def clearStr(StrValue):
        """"чистит от html кода данные"""
        return ' '.join(re.sub(r"<[^>]+>", '', StrValue).split())

    def CreateCsvFileByYear(self):
        for k in self.__DynamicsSalaryByYear.keys():
            self.CreateCsvBy(k)

    def CreateCsvBy(self, year):
        with open(f'VacanciesByYears/vanacies_from_{year}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
            for vacancy in self.__DynamicsSalaryByYear[year]:
                writer.writerow(
                    [vacancy.name, vacancy.Salary.From, vacancy.Salary.To, vacancy.Salary.Currency, vacancy.areaName,
                     vacancy.publishedAt])


class Vacancy:
    def __init__(self, info):
        self.name = info[0]
        self.Salary = Salary(float(info[1]), float(info[2]), info[3])
        self.areaName = info[4]
        x = info[5]
        self.publishedAt = datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")

    def __str__(self):
        return [self.name, self.Salary.From, self.Salary.To, self.Salary.Currency, self.publishedAt]


class Salary:
    """класс работает в данными зарплаты.

    Attributes:
         From (int) - нижняя граница вклада
         To (int) - Верхняя граница вклада
         Currency (int) - валюта
    """
    CurrencyToRub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def __init__(self, salary_from, salary_to, salary_currency):
        self.From = salary_from
        self.To = salary_to
        self.Currency = salary_currency

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return f"{Formate.ToNum(self.From)} - {Formate.ToNum(self.To)} ({self.Currency})"

    def ArithmeticalMean(self):
        """ выдаёт среднее значение от верхней и нижней границы
        """
        return (self.From * self.CurrencyToRub[self.Currency] + self.To * self.CurrencyToRub[self.Currency]) // 2


class Formate:
    """дополнительные методы связанные с изменением формата данных"""

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


if __name__ == '__main__':
    main()

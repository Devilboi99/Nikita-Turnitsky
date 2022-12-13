import csv
import multiprocessing
import re
import sys
import datetime
import cProfile

import pytz as pytz


def respone(response):
    st = StatisticsApp()
    result = response.pop(0)
    for dataset in response:
        result.DynamicsSalaryByYear = dict(
            list(result.DynamicsSalaryByYear.items()) + list(dataset.DynamicsSalaryByYear.items()))
        result.DynamicsSalaryByCity = dict(
            list(result.DynamicsSalaryByCity.items()) + list(dataset.DynamicsSalaryByCity.items()))
        result.TotalVacancies += dataset.TotalVacancies

    st.PrintDynamicsSalaryVacancyByYear(result.DynamicsSalaryByYear)
    st.PrintDynamicsFilterVacancyByYear(result.DynamicsSalaryByYear, result.Profession)
    st.printDymabicsByCity(result.DynamicsSalaryByCity, result.TotalVacancies)


def main():
    statisticsApp = StatisticsApp()
    directory = input('Введите название папки: ')
    profession = input('Введите название профессии: ')
    statisticsApp.LoadFilter(profession)
    paths = []
    for e in range(2007, 2023):
        paths.append(f"{directory}/vanacies_from_{e}.csv")
    with multiprocessing.Pool(3) as p:
        p.map_async(statisticsApp.DataPreparation, paths, callback=respone)
        p.close()
        p.join()


class DataSet:
    def __init__(self, profession, dynsy, dynsc, tv):
        self.Profession = profession
        self.DynamicsSalaryByYear = dynsy
        self.DynamicsSalaryByCity = dynsc
        self.TotalVacancies = tv


class StatisticsApp:
    """"программа, преваращющая данные в статистику"""

    def __init__(self):
        self.__Profession = ''
        self.__DynamicsSalaryByYear = {}
        self.__DynamicsSalaryByCity = {}
        self.__TotalVacancies = 0

    def DataPreparation(self, pathFile):
        """подготавливает данные для вывода статистики"""
        data = self.LoadCsvFile(pathFile)
        data = self.ConfigurateData(data)
        vacancies = self.__GetVacancies(data)
        self.__TotalVacancies += len(vacancies)
        self.__SetStatistics(vacancies)
        return DataSet(self.__Profession, self.__DynamicsSalaryByYear, self.__DynamicsSalaryByCity,
                       self.__TotalVacancies)

    def __SetStatistics(self, vacancies):
        """устанавливает данные по датам и городам"""
        print(4)
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

    @staticmethod
    def PrintDynamicsSalaryVacancyByYear(dynamicsSalaryByYear):
        """выводит данные по годам"""
        print("Динамика уровня зарплат по годам: " + str(
            {k: StatisticsApp.GetAverageSalary(v) for k, v in dynamicsSalaryByYear.items()}))
        print("Динамика количества вакансий по годам: " + str(
            {k: int(len(v)) for k, v in dynamicsSalaryByYear.items()}))

    @staticmethod
    def PrintDynamicsFilterVacancyByYear(dynamicsSalaryByYear, profession):
        """выводит данные по годам с учётом профессий"""
        print("Динамика уровня зарплат по годам для выбранной профессии: " + str(
            {k: StatisticsApp.GetAverageSalary(list(filter(lambda x: profession in x.name, v))) for k, v in
             dynamicsSalaryByYear.items()}))

        print("Динамика количества вакансий по годам для выбранной профессии: " + str(
            {k: int(len(list(filter(lambda x: profession in x.name, v)))) for k, v in
             dynamicsSalaryByYear.items()}))

    @staticmethod
    def printDymabicsByCity(DynamicsSalaryByCity, totalVac):
        """выводит данные по городам"""
        result = {k: StatisticsApp.GetAverageSalary(v) for k, v in DynamicsSalaryByCity.items() if
                  round(len(v) / totalVac, 4) >= 0.01}
        print("Уровень зарплат по городам (в порядке убывания): " + str(
            dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])))

        result = {k: round(len(v) / totalVac, 4) for k, v in DynamicsSalaryByCity.items() if
                  round(len(v) / totalVac, 4) >= 0.01}
        print("Доля вакансий по городам (в порядке убывания): " + str(
            dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])))

    @staticmethod
    def LoadCsvFile(fileName):
        print(1)
        File = open(fileName, encoding='utf_8_sig')
        data = [row for row in csv.reader(File)]
        if len(data) == 0:
            print("Пустой файл")  ## кринж
            sys.exit()
        return data

    def LoadFilter(self, profession):
        self.__Profession = profession

    @staticmethod
    def __GetVacancies(data):
        """превращает данные в стукрутру vacancy"""
        print(3)
        personsInfo = []
        for row in data:
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

    def ConfigurateData(self, data):
        """получение данных в формате для чтения"""
        print(2)
        if len(data[0]) == 6:
            data.pop(0)
            return data
        personsInfo = []
        attributes = data.pop(0)
        for row in data:
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

        return info

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
                     str(vacancy.publishedAt).replace(' ', 'T')])


class Vacancy:
    def __init__(self, info):
        self.name = info[0]
        self.Salary = Salary(float(info[1]), float(info[2]), info[3])
        self.areaName = info[4]
        x = info[5]
        native = datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
        self.publishedAt = native

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
    cProfile.run("main()");

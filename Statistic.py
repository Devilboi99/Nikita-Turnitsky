import csv
import re
import sys

from DataSet import DataSet
from Vacancy import Vacancy


class Statistics:
    """"программа, преваращющая данные в статистику"""

    def __init__(self):
        self.__DynamicsSalaryByYear = {}
        self.__DynamicsSalaryByCity = {}

    def DataPreparation(self, pathProf):
        """подготавливает данные для вывода статистики"""
        data = self.__LoadCsvFile(pathProf[0])
        data = self.ConfigurateData(data)
        vacancies = self.__GetVacancies(data)
        totalVacancies = len(vacancies)
        self.__SetStatistics(vacancies)
        return DataSet(pathProf[1], self.__DynamicsSalaryByYear, self.__DynamicsSalaryByCity,
                       totalVacancies)

    def __SetStatistics(self, vacancies):
        """устанавливает данные по датам и городам"""
        for vacancy in vacancies:
            if not self.IsAdded(vacancy.publishedAt.year, self.__DynamicsSalaryByYear):
                self.__DynamicsSalaryByYear[vacancy.publishedAt.year] = []
            if not self.IsAdded(vacancy.areaName, self.__DynamicsSalaryByCity):  ## дублируется код убрать потом
                self.__DynamicsSalaryByCity[vacancy.areaName] = []
            self.__DynamicsSalaryByYear[vacancy.publishedAt.year].append(vacancy)
            self.__DynamicsSalaryByCity[vacancy.areaName].append(vacancy)
        return

    @staticmethod
    def IsAdded(element, dynamics):
        """проверяет добавлен ли ключ"""
        return element in dynamics.keys()

    @staticmethod
    def GetDynamicsSalaryByYear(dynamicsSalaryByYear):
        """выводит данные зарплат по годам"""
        return {k: Statistics.GetAverageSalary(v) for k, v in dynamicsSalaryByYear.items()}

    @staticmethod
    def GetDynamicsVacancyByYear(dynamicsSalaryByYear):
        return {k: int(len(v)) for k, v in dynamicsSalaryByYear.items()}

    @staticmethod
    def GetDynamicsWithFilterSalaryByYear(dynamicsSalaryByYear, profession):
        return {k: Statistics.GetAverageSalary(list(filter(lambda x: profession in x.name, v))) for k, v in
                dynamicsSalaryByYear.items()}

    @staticmethod
    def GetDynamicsWithFilterVacancyByYear(dynamicsSalaryByYear, profession):
        return {k: int(len(list(filter(lambda x: profession in x.name, v)))) for k, v in
                dynamicsSalaryByYear.items()}

    @staticmethod
    def GetDynamicsSalaryByCity(DynamicsSalaryByCity, totalVac):
        """выводит данные по городам"""
        result = {k: Statistics.GetAverageSalary(v) for k, v in DynamicsSalaryByCity.items() if
                  round(len(v) / totalVac, 4) >= 0.01}

        return dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])

    @staticmethod
    def GetDynamicsProcentCountByCity(DynamicsSalaryByCity, totalVac):
        result = {k: round(len(v) / totalVac, 4) for k, v in DynamicsSalaryByCity.items() if
                  round(len(v) / totalVac, 4) >= 0.01}

        return dict(sorted(result.items(), reverse=True, key=lambda item: item[1])[:10])

    @staticmethod
    def __LoadCsvFile(fileName):
        File = open(fileName, encoding='utf_8_sig')
        data = [row for row in csv.reader(File)]
        if len(data) == 0:
            print("Пустой файл")  ## кринж
            sys.exit()
        return data

    @staticmethod
    def __GetVacancies(data):
        """превращает данные в стукрутру vacancy"""
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

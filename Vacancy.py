import datetime

from Salary import Salary


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


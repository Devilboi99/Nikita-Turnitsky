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
        return f"{self.ToNum(self.From)} - {self.ToNum(self.To)} ({self.Currency})"

    def ArithmeticalMean(self):
        """ выдаёт среднее значение от верхней и нижней границы
        """
        return (self.From * self.CurrencyToRub[self.Currency] + self.To * self.CurrencyToRub[self.Currency]) // 2

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
import multiprocessing
from Report import Report
from Statistic import Statistics as st
from DataSet import DataSet


def respone(response):
    result = response.pop(0)
    vacancies = result.TotalVacancies
    for dataset in response:
        result.DynamicsSalaryByYear = dict(
            list(result.DynamicsSalaryByYear.items()) + list(dataset.DynamicsSalaryByYear.items()))
        for k, v in dataset.DynamicsSalaryByCity.items():
            if k not in result.DynamicsSalaryByCity:
                result.DynamicsSalaryByCity[k] = []
            for e in v:
                result.DynamicsSalaryByCity[k].append(e)
        vacancies += dataset.TotalVacancies

    print("Динамика уровня зарплат по годам: " + str(st.GetDynamicsSalaryByYear(result.DynamicsSalaryByYear)))
    print("Динамика количества вакансий по годам: " + str(st.GetDynamicsVacancyByYear(result.DynamicsSalaryByYear)))
    print("Динамика уровня зарплат по годам для выбранной профессии: " +
          str(st.GetDynamicsWithFilterSalaryByYear(result.DynamicsSalaryByYear, result.Profession)))
    print("Динамика количества вакансий по годам для выбранной профессии: " +
          str(st.GetDynamicsWithFilterVacancyByYear(result.DynamicsSalaryByYear, result.Profession)))
    print("Уровень зарплат по городам (в порядке убывания): " + str(st.GetDynamicsSalaryByCity(result.DynamicsSalaryByCity, vacancies)))
    print("Доля вакансий по городам (в порядке убывания): " + str(st.GetDynamicsProcentCountByCity(result.DynamicsSalaryByCity, vacancies)))
    report = Report(result.DynamicsSalaryByYear, result.DynamicsSalaryByCity, result.Profession, vacancies)
    report.generateExcel()


def main():
    statisticsApp = st()
    directory = input('Введите название папки: ')
    profession = input('Введите название профессии: ')
    paths = []
    for e in range(2007, 2023):
        paths.append((f"{directory}/vanacies_from_{e}.csv", profession))
    with multiprocessing.Pool(10) as p:
        p.map_async(statisticsApp.DataPreparation, paths, callback=respone)
        p.close()
        p.join()


if __name__ == "__main__":
    main()

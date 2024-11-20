import csv
import os
from html import escape  # Функция для экранирования специальных HTML-символов в строках


class PriceMachine():
    def __init__(self, data_directory='data'):
        self.data_directory = data_directory  # Директория для поиска csv-файлов
        self.prices = []                      # Список для хранения данных о товарах

    def load_prices(self):
        '''
            Сканируем указанную директорию и загружаем только те CSV-файлы,
            которые содержат слово 'price' в названии
        '''
        for filename in os.listdir(self.data_directory):
            if 'price' in filename.lower() and filename.endswith('.csv'):
                self._load_file(
                    os.path.join(
                        self.data_directory,
                        filename),
                    filename)

    def _load_file(self, file_path, filename):
        '''
        Метод для загрузки данных из одного csv-файла. Открывает файл и использует csv.reader для чтения строк.
        Находит индексы нужных столбцов с помощью функции _serch_product_price_weight.
        Вычисляет цену за кг и добавляет данные в список prices
        '''
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            '''
            Открывается файл по указанному пути в режиме чтения,
            newline='' - обеспечивает правильную обработку новых строк
            '''
            reader = csv.reader(
                csvfile, delimiter=',')  # разделитель данных в csv - запятая
            # Считывает первую строку csv-файла, в которой содержатся заголовки
            # столбцов
            headers = next(reader, None)
            product_index, price_index, weight_index = self._search_product_price_weight(
                headers)

            if product_index is not None and price_index is not None and weight_index is not None:
                ''' Проверяется, что все необходимые индексы столбцов были найдены
                '''
                for row in reader:  # Перебор каждой строки и извлечение цены и веса товара
                    price = float(row[price_index])
                    weight = float(row[weight_index])
                    if weight != 0:
                        price_per_kg = price / weight    # расчет цены за 1 кг
                    else:
                        price_per_kg = float('inf')
                    self.prices.append({
                        'name': row[product_index],
                        'price': price,
                        'weight': weight,
                        'file': filename,
                        'price_per_kg': price_per_kg
                    })       # Создается словарь с информацией о продукте и добавляется в список prices

    def _search_product_price_weight(self, headers):
        '''
            Метод для поиска и возвращения номеров столбцов c названиями товара, ценами и весом.
            Перебирает заголовки и опрпеделяет индексы нужных столбцов по известным названиям
        '''
        product_index = None  # Инициилируются переменные для хранения индексов с наименованием, ценой и весом
        price_index = None
        weight_index = None

        for i, header in enumerate(
                # Возвращает пару (индекс, заголовок) для каждого заголовка в
                # списке headers
                headers):
            header_lower = header.lower()   # Перевод в нижний регистр
            # Разбивает строку заголовка на список подстрок по запятым
            header_lower = list(header_lower.split(","))
            '''
            Ниже перебирается каждая часть заголовка, чтобы проверить, соответствует ли она одному из известных
            вариантов для названия товара.Если совпадение найдено, устанавливает product_index, price_index,
            weight_index на текущий индекс i.
            '''
            for item in header_lower:
                if item in ['название', 'продукт', 'товар', 'наименование']:
                    product_index = i
            for item in header_lower:
                if item in ['цена', 'розница']:
                    price_index = i
            for item in header_lower:
                if item in ['фасовка', 'масса', 'вес']:
                    weight_index = i

        return product_index, price_index, weight_index

    def find_text(self, text):
        '''
        Метод для поиска товаров по тексту
        :param text:
        :return: список results, отсортированный по возрастанию значения price_per_kg.
        Используется анонимная функция lambda d качестве ключа сортировки
        '''
        results = []
        for entry in self.prices:         # Перебирается каждый словарь в списке price
            if text.lower() in entry['name'].lower(
                # проверяет содержится ли text в названии прордукта (нижний
                # регистр)
            ):
                results.append(entry)

        return sorted(results, key=lambda x: x['price_per_kg'])

    def display_results(self, results):
        '''
        Метод для отображения результатов поиска в консоли
        :param results:
        :return: Выводит таблицу с данными о товарах. Устанавливается предел символов для вывода данных.
        '''
        print(
            f"{
                '№':<5}{
                'Наименование':<50}{
                'Цена':<10}{
                    'вес':<10}{
                        'файл':<15}{
                            'цена за кг':<10}")
        for i, entry in enumerate(results, 1):
            print(
                f"{
                    i:<5}{
                    entry['name']:<50}{
                    entry['price']:<10}{
                    entry['weight']:<10}{
                    entry['file']:<15}{
                        entry['price_per_kg']:<10.2f}"
            )

    def export_to_html(self, results, filename='output.html'):
        '''
        Метод для экспорта результатов в HTML-файл.
        Принимает на вход список результатов поиска товаров
        выводи данные в файл output.html
        '''

        with open(filename, 'w', encoding='utf-8') as f:
            # Запись начальных тэгов страницы
            f.write('<html><head><title>Product Search Results</title></head><body>')
            # Заголовок 1-го уровня
            f.write('<h1>Результат поиска продуктов</h1>')
            # Начинает HTML-таблицу с границей, установленной на 1 пиксель
            f.write('<table border = "1">')
            '''  Добавляется строка заголовка таблицы'''
            f.write(
                '<tr><th>№</th><th>Наименование</th><th>цена</th><th>вес</th><th>файл</th><th>цена за кг.</th></tr>')

            for i, entry in enumerate(results, 1):
                ''' Перебирается каждый элемент в списке results,
                возвращается пара (индекс, элемент) для каждого элемента, начиная с индекса 1
                 '''
                f.write('<tr>')     # Начинается новая строка в таблице
                ''' Добавляютcя ячейки с названием продукта, ценой, весом, именем файла, ценой за кг.
                Экранирование с помощью escapе применяется для предотвращения XSS-уязвимостей '''
                f.write(f'<td>{i}</td>')
                f.write(f'<td>{escape(entry["name"])}</td>')
                f.write(f'<td>{entry["price"]}</td>')
                f.write(f'<td>{entry["weight"]}</td>')
                f.write(f'<td>{entry["file"]}</td>')
                f.write(f'<td>{entry["price_per_kg"]:.2f}</td>')
                f.write('</tr>')     # Закрывается текущая строка таблицы

                f.write('</table</body></html>')


def main():
    '''
    Основная функция программы. Создает объект класса PriceMashine и загружает данные
    В бесконечном цикле запрашивается текст для поиска товаров и выводятся результаты, которые сохраняются в файл html

    '''
    pm = PriceMachine()
    pm.load_prices()

    while True:
        user_input = input(
            "Введите текст для поиска (или 'exit' для выхода): ")
        if user_input.lower() == 'exit':
            print("Работа завершена")
            break
        results = pm.find_text(user_input)
        pm.display_results(results)
        pm.export_to_html(results)
        print("Результаты сохранены в файл output.html")


if __name__ == '__main__':
    main()

import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from fastapi import UploadFile


header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
          ' AppleWebKit/537.36 (KHTML, like Gecko)'
          ' Chrome/122.0.0.0 Safari/537.36'}


class Processor():
    async def check_file(self, file: UploadFile) -> UploadFile:
        df_articles, columns = self._read(file)
        parsed_df = self._parse(df_articles, columns)
        output_file = self._write(parsed_df)
        return output_file

    def _read(self, file: UploadFile) -> tuple[pd.DataFrame, list]:
        df_all = pd.read_excel(
            BytesIO(file.file.read()),
            header=0,
            engine="odf")
        column_names = df_all.columns.tolist()
        return df_all, column_names

    def get_characters(self, characters_text) -> dict:
        lines = characters_text.split('\n')
        characters_dict = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                characters_dict[key] = value
        characters_dict['Характеристики лазера'] = characters_dict[
            'Характеристики лазера'].split(', ')
        return characters_dict

    def _parse(self, df: pd.DataFrame, column_names: list) -> pd.DataFrame:
        for row in range(df.shape[0]):
            url = 'https://amo-tools.com/ru/search/?q='
            url += df.iloc[row, 0]
            url += '&s=search'
            search_response = requests.get(url, headers=header)
            soup = BeautifulSoup(search_response.text, 'lxml')
            block = soup.find('div', class_='search-page')
            items = block.find_all('div', class_='search-item')
            if len(items) != 1:
                raise Exception('Error! More than one result')
            new_url = 'https://amo-tools.com' + block.find('a').get('href')
            article_response = requests.get(new_url, headers=header)
            article_soup = BeautifulSoup(article_response.text, 'lxml')
            description = article_soup.find('div', id='tab11')
            characters_text = article_soup.find('div', id='tab2').text
            characters = self.get_characters(characters_text)
            df[column_names[2]] = description.text
            df[column_names[5]] = characters['Точность']
            df[column_names[6]] = characters['Рабочее расстояние']
            df[column_names[7]] = characters['Рабочее расстояние с приемником']
            # Придумать, откуда взять эти данные
            '''df[column_names[8]] = characters['']
            df[column_names[9]] = characters['']
            df[column_names[10]] = characters['']
            df[column_names[11]] = characters['']
            df[column_names[12]] = characters['']'''
            df[column_names[13]] = characters['Крепление под штатив']
            df[column_names[14]] = characters['Цвет лазера']
            df[column_names[15]] = characters['Источник питания']
            df[column_names[16]] = characters['Вес']
            df[column_names[17]] = characters['Размеры']
            df[column_names[18]] = characters['Рабочая температура']
            # Что вообще значит "время измерения"?
            '''df[column_names[19]] = characters['']'''
            df[column_names[20]] = characters['Время непрерывной работы']
            df[column_names[21]] = characters['Характеристики лазера'][1]
            df[column_names[22]] = characters['Диапазон самовыравнивания']
            df[column_names[23]] = characters['Характеристики лазера'][0]
            print(characters_text)
            for i in range(0, 28):
                print(df[column_names[i]].name + ':',
                      df[column_names[i]].values[0])
        return df

    def _write(self, df: pd.DataFrame) -> UploadFile:
        output_file = BytesIO()
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        output_file.seek(0)
        path_file = './examples/output.xlsx'
        with pd.ExcelWriter(path_file) as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        return UploadFile(output_file, filename="output.xlsx")


processor: Processor = Processor()

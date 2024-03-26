import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from fastapi import UploadFile
from starlette.responses import JSONResponse


header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
          ' AppleWebKit/537.36 (KHTML, like Gecko)'
          ' Chrome/122.0.0.0 Safari/537.36'}


class Processor():
    async def check_file(self, file: UploadFile) -> JSONResponse:
        df_articles, columns = self._read(file)
        await self._parse(df_articles, columns)
        return JSONResponse({"message": "Success"})

    def _read(self, file: UploadFile) -> tuple[pd.DataFrame, list]:
        df_all = pd.read_excel(
            BytesIO(file.file.read()),
            header=0,
            engine="odf")
        column_names = df_all.columns.tolist()
        return df_all, column_names

    def _parse(self, df: pd.DataFrame, column_names: list) -> None:
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
            print(new_url)
            print(article_response.text)
            article_soup = BeautifulSoup(article_response.text, 'lxml')
            characters = article_soup.find('div', id='tab2')
            print(characters.text)

    def _write(self, df: pd.DataFrame) -> UploadFile:
        output_file = BytesIO()
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        output_file.seek(0)
        return UploadFile(output_file, filename="output.xlsx")


processor: Processor = Processor()

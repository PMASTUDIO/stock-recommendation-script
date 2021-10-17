import requests
import string
from bs4 import BeautifulSoup

pages_ext = list(string.ascii_uppercase) + ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

stocks_symbols = []

print("Downloading of B3 stocks started...")

for idx, ext in enumerate(pages_ext):
  URL = "https://br.advfn.com/bolsa-de-valores/bovespa/" + str(ext)
  page = requests.get(URL)

  soup = BeautifulSoup(page.content, "html.parser")

  for symbol_soup in soup.select('td.String.Column2.ColumnLast'):
    stocks_symbols.append(symbol_soup.get_text())
  
  percentage_downloaded = (idx / len(pages_ext)) * 100
  print("Downloaded: " + str(int(percentage_downloaded)) + "%")

print("Downloading of B3 BDRS started...")

def download_bdrs():
  URL = "https://investnews.com.br/financas/veja-a-lista-completa-dos-bdrs-disponiveis-para-pessoas-fisicas-na-b3/"
  page = requests.get(URL)

  soup = BeautifulSoup(page.content, "html.parser")

  for symbol_soup in soup.select('td:nth-child(2)'):
    stocks_symbols.append(symbol_soup.get_text())


download_bdrs()
print("Writing to file...")

with open("symbols_watchlist.txt", "w") as out:
  for symbol in stocks_symbols:  
    out.write(symbol + ".SA" + "\n")

print("Done!")
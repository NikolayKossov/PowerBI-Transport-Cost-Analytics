# Analiza w Excelu

Nie dołączono skoroszytu ani tabel przestawnych; to instrukcja dodatkowego ćwiczenia.

1. Dane → Pobierz dane → Z tekstu/CSV: zaimportuj data/curated/Transport.csv i wymiary. Ustaw typy, identyfikatory jako tekst.
2. Załaduj do modelu danych i utwórz relacje według docs/model.md.
3. Utwórz tabelę przestawną: miesiąc w wierszach, segment/kierunek/linia w kolumnach, sumy kosztów i wolumenów jako wartości.
4. Wskaźniki kosztu jednostkowego licz jako iloraz sum, nigdy średnią kosztów jednostkowych.
5. Przećwicz SUMIFS/SUMA.WARUNKÓW, XLOOKUP/X.WYSZUKAJ oraz IFERROR/JEŻELI.BŁĄD dla uzgodnienia ze źródłem.
6. Odśwież wszystkie po podmianie źródeł i porównaj z docs/control-totals.json.

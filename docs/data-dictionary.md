# Słownik danych

| Tabela | Pole | Typ źródła | Znaczenie / jednostka |
|---|---|---|---|
| fx | `Date` | str | ISO 8601 |
| fx | `Currency` | str | patrz metodyka i nazwa pola |
| fx | `RateToPLN` | float | PLN, bez VAT |
| shipments | `ShipmentID` | str | klucz |
| shipments | `Date` | str | ISO 8601 |
| shipments | `RouteID` | str | klucz |
| shipments | `ClientID` | str | klucz |
| shipments | `CarrierID` | str | klucz |
| shipments | `Pallets` | int | patrz metodyka i nazwa pola |
| shipments | `CapacityPallets` | int | patrz metodyka i nazwa pola |
| shipments | `DistanceKm` | int | patrz metodyka i nazwa pola |
| shipments | `Deliveries` | int | patrz metodyka i nazwa pola |
| shipments | `OnTime` | int | patrz metodyka i nazwa pola |
| invoices | `ShipmentID` | str | klucz |
| invoices | `Currency` | str | patrz metodyka i nazwa pola |
| invoices | `Base` | float | patrz metodyka i nazwa pola |
| invoices | `Fuel` | float | patrz metodyka i nazwa pola |
| invoices | `Toll` | float | patrz metodyka i nazwa pola |
| Date | `Date` | str | ISO 8601 |
| Date | `Year` | int | patrz metodyka i nazwa pola |
| Date | `Month` | int | patrz metodyka i nazwa pola |
| Date | `YearMonth` | str | patrz metodyka i nazwa pola |
| Date | `Quarter` | str | patrz metodyka i nazwa pola |
| Client | `ClientID` | str | klucz |
| Client | `Client` | str | patrz metodyka i nazwa pola |
| Client | `Segment` | str | patrz metodyka i nazwa pola |
| Client | `Market` | str | patrz metodyka i nazwa pola |
| Route | `RouteID` | str | klucz |
| Route | `Route` | str | patrz metodyka i nazwa pola |
| Route | `Market` | str | patrz metodyka i nazwa pola |
| Route | `Scope` | str | patrz metodyka i nazwa pola |
| Route | `DistanceKm` | int | patrz metodyka i nazwa pola |
| Route | `BudgetPLNPerKm` | float | PLN, bez VAT |
| Carrier | `CarrierID` | str | klucz |
| Carrier | `Carrier` | str | patrz metodyka i nazwa pola |
| Transport | `ShipmentID` | str | klucz |
| Transport | `Date` | str | ISO 8601 |
| Transport | `RouteID` | str | klucz |
| Transport | `ClientID` | str | klucz |
| Transport | `CarrierID` | str | klucz |
| Transport | `Pallets` | int | patrz metodyka i nazwa pola |
| Transport | `CapacityPallets` | int | patrz metodyka i nazwa pola |
| Transport | `DistanceKm` | int | patrz metodyka i nazwa pola |
| Transport | `Deliveries` | int | patrz metodyka i nazwa pola |
| Transport | `OnTime` | int | patrz metodyka i nazwa pola |
| Transport | `ActualCostPLN` | float | PLN, bez VAT |
| Transport | `BudgetCostPLN` | float | PLN, bez VAT |
| Transport | `LoadedPalletKm` | int | patrz metodyka i nazwa pola |
| Transport | `CapacityPalletKm` | int | patrz metodyka i nazwa pola |

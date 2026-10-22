let
    Source = Csv.Document(File.Contents(DataRoot & "/raw/invoices.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"ShipmentID", type text}, {"Currency", type text}, {"Base", type number}, {"Fuel", type number}, {"Toll", type number}}, "en-US")
in
    Typed

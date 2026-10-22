let
    Source = Csv.Document(File.Contents(DataRoot & "/raw/fx.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Date", type date}, {"Currency", type text}, {"RateToPLN", type number}}, "en-US")
in
    Typed

let
    Source = Csv.Document(File.Contents(DataRoot & "/dimensions/Date.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Date", type date}, {"Year", Int64.Type}, {"Month", Int64.Type}, {"YearMonth", type text}, {"Quarter", type text}}, "en-US")
in
    Typed

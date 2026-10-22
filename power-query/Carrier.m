let
    Source = Csv.Document(File.Contents(DataRoot & "/dimensions/Carrier.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"CarrierID", type text}, {"Carrier", type text}}, "en-US")
in
    Typed

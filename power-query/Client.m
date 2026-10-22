let
    Source = Csv.Document(File.Contents(DataRoot & "/dimensions/Client.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"ClientID", type text}, {"Client", type text}, {"Segment", type text}, {"Market", type text}}, "en-US")
in
    Typed

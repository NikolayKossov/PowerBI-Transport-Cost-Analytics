let
    Source = Csv.Document(File.Contents(DataRoot & "/dimensions/Route.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"RouteID", type text}, {"Route", type text}, {"Market", type text}, {"Scope", type text}, {"DistanceKm", Int64.Type}, {"BudgetPLNPerKm", type number}}, "en-US")
in
    Typed

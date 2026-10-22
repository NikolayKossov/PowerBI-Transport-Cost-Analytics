let
    Source = Csv.Document(File.Contents(DataRoot & "/raw/shipments.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"ShipmentID", type text}, {"Date", type date}, {"RouteID", type text}, {"ClientID", type text}, {"CarrierID", type text}, {"Pallets", Int64.Type}, {"CapacityPallets", Int64.Type}, {"DistanceKm", Int64.Type}, {"Deliveries", Int64.Type}, {"OnTime", Int64.Type}}, "en-US")
in
    Typed

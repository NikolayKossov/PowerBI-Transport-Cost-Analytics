let
    A = Table.NestedJoin(stg_shipments, {"ShipmentID"}, stg_invoices, {"ShipmentID"}, "Invoice", JoinKind.LeftOuter),
    B = Table.ExpandTableColumn(A, "Invoice", {"Currency", "Base", "Fuel", "Toll"}),
    C = Table.NestedJoin(B, {"Date", "Currency"}, stg_fx, {"Date", "Currency"}, "FX", JoinKind.LeftOuter),
    D = Table.ExpandTableColumn(C, "FX", {"RateToPLN"}),
    E = Table.NestedJoin(D, {"RouteID"}, Route, {"RouteID"}, "RouteBudget", JoinKind.LeftOuter),
    F = Table.ExpandTableColumn(E, "RouteBudget", {"BudgetPLNPerKm"}),
    Checked = if Table.RowCount(F) <> Table.RowCount(stg_shipments) or List.Contains(F[RateToPLN], null) or List.Contains(F[Base], null) or List.Contains(F[BudgetPLNPerKm], null) then error "Missing/duplicate invoice, route or FX key" else F,
    G = Table.AddColumn(Checked, "ActualCostPLN", each Number.Round(([Base]+[Fuel]+[Toll])*[RateToPLN], 2), type number),
    H = Table.AddColumn(G, "BudgetCostPLN", each Number.Round([DistanceKm]*[BudgetPLNPerKm], 2), type number),
    I = Table.AddColumn(H, "LoadedPalletKm", each [Pallets]*[DistanceKm], Int64.Type),
    J = Table.AddColumn(I, "CapacityPalletKm", each [CapacityPallets]*[DistanceKm], Int64.Type)
in J

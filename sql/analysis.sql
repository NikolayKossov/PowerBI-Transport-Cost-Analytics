-- SQLite; run: python scripts/validate.py
-- Read-only analysis of the independently loaded curated tables.
SELECT r.Market, substr(t.Date,1,7) AS Month, COUNT(*) AS Shipments, SUM(t.ActualCostPLN) AS CostPLN, SUM(t.ActualCostPLN-t.BudgetCostPLN) AS VariancePLN, 1.0*SUM(t.LoadedPalletKm)/NULLIF(SUM(t.CapacityPalletKm),0) AS Utilization FROM Transport t JOIN Route r ON t.RouteID=r.RouteID GROUP BY r.Market, substr(t.Date,1,7);

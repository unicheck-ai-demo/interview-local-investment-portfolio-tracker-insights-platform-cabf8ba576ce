# Interview Tasks

## Task 1: Branch Locator Radius Bug

When using the "nearest branches" feature, the system sometimes fails to return branches that are within the specified radius in kilometers. Review and fix the issue so that the search radius parameter (in kilometers) correctly filters nearby institutions based on the intended distance.

## Task 2: Portfolio Performance Query Efficiency

When requesting portfolio performance for a given portfolio, the system executes multiple database queries, causing performance issues under heavy load. Refactor the service so that both the average price and total amount are fetched in a single database call.

## Task 3: Portfolio Holdings Breakdown Feature

Users would like to see a detailed breakdown of asset holdings within a portfolio. Implement an endpoint that returns, for a given portfolio, a collection of assets with the total amount held for each asset. Each entry in the response should include the asset name and the summed amount. Ensure the response is sorted by asset name.
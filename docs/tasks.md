# Interview Tasks

## Task 1: Branch Locator Radius Bug

When using the "nearest branches" feature, the system sometimes fails to return branches that are within the specified radius in kilometers. Review and fix the issue so that the search radius parameter (in kilometers) correctly filters nearby institutions based on the intended distance.

## Task 2: Portfolio Performance Query Efficiency

When requesting portfolio performance for a given portfolio, the system executes multiple database queries, causing performance issues under heavy load. Refactor the service so that both the average price and total amount are fetched in a single database call.
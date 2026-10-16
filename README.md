# Legacy Portfolio Planner - online settings

Every copy of the planner reads planner-settings.json from this repository each time it refreshes prices.

- latest_version: raise it (e.g. 2.1) when you release a new version. Buyers on an older version see a red notice at the top of their Dashboard.
- download_url: where buyers get the new version. The notice links here.
- message: optional one-line note shown on the Dashboard (leave empty for none).
- ngx_equities_url, ngx_ticker_url: NGX price links. Change only if the exchange moves its data service.
- yahoo_chart_url: global price link. Change only if Yahoo moves it.

Rules: keep the file valid JSON (commas and quotes). Leave a field empty to use the link built into the planner. Changes reach buyers at their next refresh (GitHub may take up to 5 minutes).

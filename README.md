# Legacy Portfolio Planner - online settings

Every copy of the planner (the Excel workbook and the app) reads planner-settings.json from this repository each time it refreshes prices.

## planner-settings.json

Excel planner:
- latest_version: raise it (e.g. 2.1) when you release a new workbook version. Buyers on an older version see a red notice at the top of their Dashboard.
- download_url: where buyers get the new workbook. The notice links here.
- message: optional one-line note shown on the Dashboard (leave empty for none).
- ngx_equities_url, ngx_ticker_url: NGX price links. Change only if the exchange moves its data service.
- fx_url: Central Bank of Nigeria exchange-rate link. Change only if the CBN moves it.

App (Windows, Mac and web):
- app_latest_version: raise it (e.g. 2.0.1) when you publish a new app release. Older apps show a "new version available" notice.
- app_download_url: where that notice sends buyers (the latest release page).
- buy_url: the "Get a licence" link on the activation screen.
- prices_json_url: the price file the web app reads (prices.json below).

Rules: keep the file valid JSON (commas and quotes). Leave a field empty to use the link built into the planner. Changes reach buyers at their next refresh (GitHub may take up to 5 minutes).

## prices.json (updated automatically)

The "Update prices" action (.github/workflows/update-prices.yml) runs scripts/fetch_prices.py every 30 minutes during NGX trading hours on weekdays, after the close and once at night. It saves the latest NGX share, fund and ETF prices, the official CBN exchange rates and the Brent oil price to prices.json.

Brent oil (ticker BZ=F in the planner) is the U.S. Energy Information Administration's Europe Brent spot price, read from FRED (St. Louis Fed) with EIA's own page as a backup. It is public-domain U.S. government data, credited in the file's "credits" section. EIA publishes it weekly, so it runs a few days behind the market.

Data rule: only add sources whose terms allow use in a paid product. Free plans from Yahoo Finance, Alpha Vantage, Twelve Data, FMP and similar are for personal use only. Index values (S&P 500, Nasdaq) need the index owner's permission. US ETF, offshore fund and gold prices need a paid redistribution licence. The web app uses this file because browsers cannot read the NGX and CBN sites directly; the desktop apps fetch prices directly and use this file only as a fallback.

To run it by hand: Actions tab > Update prices > Run workflow.

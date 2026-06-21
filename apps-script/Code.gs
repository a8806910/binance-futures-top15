const BINANCE_EXCHANGE_INFO_URL = 'https://fapi.binance.com/fapi/v1/exchangeInfo';
const BINANCE_TICKER_24H_URL = 'https://fapi.binance.com/fapi/v1/ticker/24hr';
const LATEST_SHEET_NAME = '最新榜单';
const HISTORY_SHEET_NAME = '历史记录';

function updateBinanceTop15() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) {
    throw new Error('另一次抓取仍在运行，本次已跳过。');
  }

  try {
    const responses = UrlFetchApp.fetchAll([
      { url: BINANCE_EXCHANGE_INFO_URL, muteHttpExceptions: true },
      { url: BINANCE_TICKER_24H_URL, muteHttpExceptions: true },
    ]);
    responses.forEach((response, index) => {
      if (response.getResponseCode() !== 200) {
        throw new Error(`币安接口请求失败：${index === 0 ? 'exchangeInfo' : 'ticker/24hr'}，HTTP ${response.getResponseCode()}`);
      }
    });

    const exchangeInfo = JSON.parse(responses[0].getContentText());
    const tickers = JSON.parse(responses[1].getContentText());
    const eligible = new Set(
      exchangeInfo.symbols
        .filter(symbol =>
          symbol.status === 'TRADING' &&
          symbol.contractType === 'PERPETUAL' &&
          symbol.quoteAsset === 'USDT' &&
          symbol.marginAsset === 'USDT'
        )
        .map(symbol => symbol.symbol)
    );

    const top15 = tickers
      .filter(ticker => eligible.has(ticker.symbol))
      .map(ticker => ({
        symbol: ticker.symbol,
        change: Number(ticker.priceChangePercent),
      }))
      .filter(row => Number.isFinite(row.change))
      .sort((a, b) => b.change - a.change)
      .slice(0, 15);

    if (top15.length !== 15) {
      throw new Error(`有效合约不足 15 个，实际为 ${top15.length} 个。`);
    }

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const latest = spreadsheet.getSheetByName(LATEST_SHEET_NAME);
    const history = spreadsheet.getSheetByName(HISTORY_SHEET_NAME);
    if (!latest || !history) {
      throw new Error('找不到“最新榜单”或“历史记录”工作表。');
    }

    const timestamp = Utilities.formatDate(new Date(), 'Asia/Shanghai', 'yyyy-MM-dd HH:mm');
    const latestRows = top15.map((row, index) => [index + 1, row.symbol, row.change / 100]);

    latest.getRange('B2').setValue(timestamp);
    latest.getRange(6, 1, 15, 3).setValues(latestRows);
    latest.getRange('C6:C20').setNumberFormat('0.00%');

    if (history.getLastRow() === 2 && String(history.getRange('A2').getValue()).startsWith('首次运行后')) {
      history.getRange('A2:D2').clearContent();
    }
    const historyRows = top15.map((row, index) => [timestamp, index + 1, row.symbol, row.change / 100]);
    const startRow = Math.max(history.getLastRow() + 1, 2);
    history.getRange(startRow, 1, historyRows.length, 4).setValues(historyRows);
    history.getRange(startRow, 4, historyRows.length, 1).setNumberFormat('0.00%');
  } finally {
    lock.releaseLock();
  }
}

function setupHourlyAutomation() {
  ScriptApp.getProjectTriggers()
    .filter(trigger => trigger.getHandlerFunction() === 'updateBinanceTop15')
    .forEach(trigger => ScriptApp.deleteTrigger(trigger));

  ScriptApp.newTrigger('updateBinanceTop15')
    .timeBased()
    .everyHours(1)
    .create();

  updateBinanceTop15();
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('币安自动化')
    .addItem('立即刷新', 'updateBinanceTop15')
    .addItem('重新安装每小时触发器', 'setupHourlyAutomation')
    .addToUi();
}

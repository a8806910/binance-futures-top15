# 币安合约涨幅前 15

GitHub Actions 云端自动化。默认每小时第 17 分钟读取币安 USD-M Futures 官方接口，并把报告追加到同一个 GitHub Issue；电脑和 Codex 均无需保持开启。

## 发布

1. 在 GitHub 新建一个仓库，将本目录推送到默认分支。
2. 在仓库的 **Actions** 页面启用工作流。
3. 打开 **币安合约涨幅前15** 工作流，先执行一次 **Run workflow**。
4. 首次成功后，仓库会自动出现 `币安合约涨幅前15｜自动汇总` Issue。后续每次结果都会成为一条新评论。

工作流使用仓库自带的 `GITHUB_TOKEN`，无需配置币安 API Key 或额外密钥。若要改变频率，修改 [`.github/workflows/binance-top15.yml`](.github/workflows/binance-top15.yml) 中的 `cron`。

## 本地验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/binance_top15.py
```

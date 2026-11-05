# 工序查查站（gxccz.cn）

机加工工序库 + 加工费计算器，静态站（仓库根＝站点根，Cloudflare Pages 直发，无构建步骤）。

- 内容数据只在 `scripts/site_data.py` 一份；改完跑 `python3 scripts/build.py` 重新生成全部页面，再推送。
- 费率口径红线：只写参考区间＋影响因素，标注来源与日期（页面统一「2026 年 11 月整理」），不写全国统一标准价。
- 域名状态：gxccz.cn 尚未加入 Cloudflare（zone 待用户在 CF 后台手动添加＋腾讯云改 NS），当前先以 Pages 子域上线；canonical/og/sitemap 已按 https://gxccz.cn 写死（最终形态）。
- 首页已预埋账号级 GSC meta 与 Bing msvalidate（与站群同账号），平台验证待 zone 就绪后由 danny 操作。

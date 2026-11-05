# BUILD-NOTES — gxccz（工序查查站）

Built 2026-11-05（用户当日拍板建站）。数据源：2026-11-04 关键词调研与方向评估
（~/workspace/your_files/gxccz-工序查查站-关键词调研-2026-11-04.md 等），首批 30 词全覆盖：
- 计算器页 /calculator/ 覆盖 #1 加工费计算器、#2 CNC加工费计算器（通用模块）、#3 线切割加工费计算器（面积法模块）
- 工序页 23 个 /gongxu/<slug>/ 覆盖词单其余工序词
- 问答页 4 个 /wenda/<slug>/：激光切割多少钱一米、攻丝多少钱一个孔、CNC加工一个零件多少钱、机械加工报价计算方法

结构：scripts/site_data.py（唯一数据源）→ scripts/build.py 渲染到仓库根。
每工序页：结论先行＋是什么＋计价方式/公式＋参考区间表＋口径声明＋影响因素＋FAQ＋FAQPage JSON-LD。

待办：
1. 用户在 Cloudflare 后台 Add Site: gxccz.cn，并在腾讯云把 NS 改到 CF 分配值；之后 danny 绑 Pages 自定义域（apex＋www）。
2. zone 就绪后做 GSC/Bing 验证并提交 sitemap（meta 已预埋）。
3. 已纳入每日 SEO 体系的工具站周节奏：周二/周五写长尾新页（词须先经用户确认，沿用 approved-keywords 流程）。
4. 联系邮箱未定，/about/ 先留占位；gxccz.com 的 Zoho 邮箱是冷邮件专用，禁止用于本站。
5. 观察期 4–6 周（自正式域名解析起算更准）：看 GSC/百度收录与展现，无量止损、域名恢复挂售。

部署触发：2026-11-05 首推在建项目之前，本次小提交用于触发 Pages 首次构建。

## 2026-11-05 基准域名切换为 pages.dev 试运行（用户当日拍板）

- 用户改定：先用 https://gxccz.pages.dev 跑收录观察期，gxccz.cn 自定义域名后补（zone/NS 仍待用户在 CF 后台处理，见待办 1）。
- 基准 URL 单一配置点：`scripts/site_data.py` 的 `SITE["domain"]`，build.py 全部 canonical/og/sitemap/robots/llms/JSON-LD 都由它生成。本次已由 https://gxccz.cn 改为 https://gxccz.pages.dev 并重建推送。
- 日后绑定 gxccz.cn 自定义域名时：把该值改回 https://gxccz.cn → 跑 `python3 scripts/build.py` → 推送，即完成切回，不要逐文件改。
- 页面页脚与关于页里的「工序查查站 gxccz.cn」为品牌文字提及，非 URL 引用，试运行期保留不动。

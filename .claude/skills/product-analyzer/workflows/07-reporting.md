# 07 Reporting

目标:每步有阶段报告,最后汇总成结构稳定的中文产品分析报告。

## 阶段报告

每个 `steps/*.md` 必须包含:
- 步骤结论。
- 操作证据:截图、URL、安装日志或错误。
- 决策依据。
- 对下一步的影响。

阶段报告要短而具体,不写空话。

## 最终报告

最终 `report.md` 使用 `REPORT_TEMPLATE.md` 的结构。必有章节顺序不能变:

1. 详细的产品逻辑介绍
2. UI/UX 风格和质量描述
3. 官网描述
4. 附录 A 截图索引

模板里的可选章节只有有证据时保留。

## 证据规则

- 所有评价必须能回到截图、官网原文或阶段报告。
- 所有保留截图必须在阶段报告或最终报告中被引用。
- 官网原文短引用即可,标注来源位置。
- 不写“流畅”“美观”“强大”这类不可证伪词;改写成具体观察。

## metadata

结束前补齐:
- `finished_at`
- `mode`
- `screenshots[]`
- `warnings[]`
- `clients`
- `android.mode`

## 收尾检查

运行或手动完成等价检查:
- `workflow.json` 合法。
- required steps 已完成或明确 skipped。
- `report.md` 存在且足够长。
- `metadata.mode` 和 `metadata.finished_at` 已写。
- 截图路径存在且被引用。

#!/usr/bin/env python3
"""
提取研究任務的 QMD (Quality-Maturity-Difficulty) 指標
並生成 QMD 記錄文件

**修正版：** 標準化 Quality 權重，確保在 0-1 範圍內
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

def extract_qmd_from_report(report_path: Path) -> Optional[Dict]:
    """
    從研究報告中提取 QMD 指標
    """
    if not report_path.exists():
        return None

    content = report_path.read_text(encoding='utf-8')

    # QMD 指標分析
    qmd = {
        'task_id': report_path.parent.name,
        'report_path': str(report_path),
        'quality': 0.0,  # 研究品質 (0-1)
        'maturity': 0.0,  # 技術成熟度 (0-1)
        'difficulty': 0.0,  # 複雜度 (0-1)
        'confidence': 'medium',  # 信心度 (low/medium/high)
        'source_count': 0,  # 數據源數量
        'section_count': 0,  # 章節數量
        'code_examples': 0,  # 代碼範例數量
        'mathematical_depth': 0,  # 數學深度 (0-3)
        'empirical_validation': False,  # 實證驗證
    }

    # 1. Quality (研究品質) - 基於多個因子（權重總和 = 1.0）
    quality_factors = []

    # 章節完整性 (權重 0.3) - 檢查標準章節
    standard_sections = [
        '執行摘要', '摘要', '核心摘要', 'introduction', 'abstract',
        '理論基礎', '方法', '核心思想', 'methodology', 'approach',
        '實證', '實驗', 'empirical', 'experiment', 'results',
        '結論', '應用', '結論', 'conclusion', 'applications',
        '局限性', 'limitations', 'discussion'
    ]
    found_sections = sum(1 for section in standard_sections if section.lower() in content.lower())
    section_score = min(found_sections / len(standard_sections), 1.0)
    quality_factors.append(section_score * 0.3)

    # 數學深度 (權重 0.2) - 檢查公式、符號
    math_indicators = ['\\[', '\\(', 'equation', '公式', '公式化', 'theorem', '引理', '證明', 'proof']
    math_depth = sum(1 for indicator in math_indicators if indicator.lower() in content.lower())
    math_score = min(math_depth / len(math_indicators), 1.0)
    qmd['mathematical_depth'] = min(math_depth, 3)
    quality_factors.append(math_score * 0.2)

    # 實證驗證 (權重 0.2) - 檢查實驗、驗證、測試
    empirical_indicators = ['實證', '實驗', '驗證', '測試', 'empirical', 'experiment', 'validation', 'test', 'benchmark']
    empirical_found = any(indicator.lower() in content.lower() for indicator in empirical_indicators)
    qmd['empirical_validation'] = empirical_found
    # ✅ 修正：添加權重 0.2（之前沒有權重，直接加 1.0）
    quality_factors.append(0.2 if empirical_found else 0.1)

    # 代碼範例 (權重 0.2) - 檢查代碼塊
    code_blocks = len(re.findall(r'```[a-z]*\n.*?```', content, re.DOTALL))
    qmd['code_examples'] = code_blocks
    quality_factors.append(min(code_blocks / 3, 1.0) * 0.2)

    # 章節數量 (權重 0.1) - 評估文檔結構
    qmd['section_count'] = len(re.findall(r'^#+\s+', content, re.MULTILINE))
    quality_factors.append(min(qmd['section_count'] / 10, 1.0) * 0.1)

    # ✅ 驗證權重總和
    total_weight = 0.3 + 0.2 + 0.2 + 0.2 + 0.1  # = 1.0

    # 計算 Quality（現在應該在 0-1 之間）
    qmd['quality'] = round(sum(quality_factors), 2)

    # 安全檢查：確保 Quality 在 0-1 範圍內
    if qmd['quality'] > 1.0:
        print(f"⚠️  Warning: Quality {qmd['quality']} > 1.0 for {qmd['task_id']}")
        qmd['quality'] = 1.0
    elif qmd['quality'] < 0.0:
        print(f"⚠️  Warning: Quality {qmd['quality']} < 0.0 for {qmd['task_id']}")
        qmd['quality'] = 0.0

    # 2. Maturity (技術成熟度) - 基於開源、實現、工具
    maturity_factors = []

    # 開源資源 (權重 0.4)
    if 'github' in content.lower() or '開源' in content:
        maturity_factors.append(0.4)
    else:
        maturity_factors.append(0.0)

    # 實現性 (權重 0.4)
    implementation_indicators = ['實現', '實作', 'implementation', 'code', '代碼', '可部署']
    if any(indicator.lower() in content.lower() for indicator in implementation_indicators):
        maturity_factors.append(0.4)
    else:
        maturity_factors.append(0.0)

    # 工具可用性 (權重 0.2)
    tool_indicators = ['工具', '套件', 'package', 'library', 'framework', 'api']
    if any(indicator.lower() in content.lower() for indicator in tool_indicators):
        maturity_factors.append(0.2)
    else:
        maturity_factors.append(0.0)

    # 計算 Maturity
    qmd['maturity'] = round(sum(maturity_factors), 2)

    # 安全檢查：確保 Maturity 在 0-1 範圍內
    if qmd['maturity'] > 1.0:
        qmd['maturity'] = 1.0
    elif qmd['maturity'] < 0.0:
        qmd['maturity'] = 0.0

    # 3. Difficulty (複雜度) - 基於數學複雜度、技術深度
    difficulty_factors = []

    # 數學複雜度 (權重 0.5)
    if qmd['mathematical_depth'] >= 2:
        difficulty_factors.append(0.5)
    elif qmd['mathematical_depth'] >= 1:
        difficulty_factors.append(0.3)
    else:
        difficulty_factors.append(0.1)

    # 技術深度 (權重 0.3)
    technical_keywords = ['neural', 'network', '深度', 'deep', 'quantum', 'quantum', 'distributed', '分散', 'concurrent', '並發']
    if any(keyword.lower() in content.lower() for keyword in technical_keywords):
        difficulty_factors.append(0.3)
    else:
        difficulty_factors.append(0.1)

    # 文檔長度 (權重 0.2)
    content_length = len(content)
    if content_length > 20000:
        difficulty_factors.append(0.2)
    elif content_length > 10000:
        difficulty_factors.append(0.1)
    else:
        difficulty_factors.append(0.0)

    # 計算 Difficulty
    qmd['difficulty'] = round(sum(difficulty_factors), 2)

    # 安全檢查：確保 Difficulty 在 0-1 範圍內
    if qmd['difficulty'] > 1.0:
        qmd['difficulty'] = 1.0
    elif qmd['difficulty'] < 0.0:
        qmd['difficulty'] = 0.0

    # 4. Confidence (信心度)
    confidence_pattern = r'(信心度|置信度|confidence)[：:：]\s*(low|medium|high|低|中|高)'
    match = re.search(confidence_pattern, content, re.IGNORECASE)
    if match:
        confidence_value = match.group(2).lower()
        if confidence_value in ['low', '低']:
            qmd['confidence'] = 'low'
        elif confidence_value in ['high', '高']:
            qmd['confidence'] = 'high'
        else:
            qmd['confidence'] = 'medium'
    else:
        # 根據 Quality 和 Maturity 推斷
        if qmd['quality'] > 0.8 and qmd['maturity'] > 0.7:
            qmd['confidence'] = 'high'
        elif qmd['quality'] > 0.6:
            qmd['confidence'] = 'medium'
        else:
            qmd['confidence'] = 'low'

    # 5. Source Count (數據源數量)
    source_pattern = r'(來源|source|數據源|data source)[：:：]\s*(\d+)'
    match = re.search(source_pattern, content, re.IGNORECASE)
    if match:
        qmd['source_count'] = int(match.group(1))
    else:
        # 推斷數據源數量
        if 'arxiv' in content.lower():
            qmd['source_count'] += 1
        if 'github' in content.lower():
            qmd['source_count'] += 1
        if 'reference' in content.lower() or '參考文獻' in content:
            qmd['source_count'] += 1

    return qmd

def generate_qmd_record(qmd: Dict, output_dir: Path) -> Path:
    """
    生成 QMD 記錄文件
    """
    task_id = qmd['task_id']

    # Markdown 格式的 QMD 記錄
    md_content = f"""# QMD 記錄：{task_id}

> **任務 ID：** {task_id}
> **報告路徑：** {qmd['report_path']}
> **生成時間：** {datetime.now().isoformat()}

---

## QMD 指標

| 指標 | 數值 | 說明 |
|------|------|------|
| **Quality (品質)** | {qmd['quality']:.2f} | 研究品質 (0-1) |
| **Maturity (成熟度)** | {qmd['maturity']:.2f} | 技術成熟度 (0-1) |
| **Difficulty (複雜度)** | {qmd['difficulty']:.2f} | 複雜度 (0-1) |
| **QMD 向量** | ({qmd['quality']:.2f}, {qmd['maturity']:.2f}, {qmd['difficulty']:.2f}) | 三維向量表示 |

---

## 詳細指標

### Quality (研究品質)
**數值：** {qmd['quality']:.2f}

**評估因子：**
- 章節完整性：{qmd['section_count']} 個章節（權重 0.3）
- 數學深度：{qmd['mathematical_depth']}/3（權重 0.2）
- 實證驗證：{'✅' if qmd['empirical_validation'] else '❌'}（權重 0.2）
- 代碼範例：{qmd['code_examples']} 個（權重 0.2）
- 章節數量：{qmd['section_count']} 個（權重 0.1）

**評級：**
- {qmd['quality']:.2f} >= 0.8: 🟢 優秀
- 0.6 <= {qmd['quality']:.2f} < 0.8: 🟡 良好
- {qmd['quality']:.2f} < 0.6: 🔴 需要改進

### Maturity (技術成熟度)
**數值：** {qmd['maturity']:.2f}

**評估因子：**
- 開源資源：{'✅' if 'github' in qmd['report_path'].lower() else '❌'}（權重 0.4）
- 實現性：檢查實現相關關鍵詞（權重 0.4）
- 工具可用性：檢查工具相關關鍵詞（權重 0.2）

**評級：**
- {qmd['maturity']:.2f} >= 0.7: 🟢 成熟（可實施）
- 0.4 <= {qmd['maturity']:.2f} < 0.7: 🟡 部分成熟（需要更多實驗）
- {qmd['maturity']:.2f} < 0.4: 🔴 早期階段（概念驗證）

### Difficulty (複雜度)
**數值：** {qmd['difficulty']:.2f}

**評估因子：**
- 數學複雜度：{qmd['mathematical_depth']}/3（權重 0.5）
- 技術深度：檢查關鍵詞（權重 0.3）
- 文檔長度：基於報告長度（權重 0.2）

**評級：**
- {qmd['difficulty']:.2f} >= 0.7: 🟢 高複雜度（需要專業知識）
- 0.4 <= {qmd['difficulty']:.2f} < 0.7: 🟡 中等複雜度
- {qmd['difficulty']:.2f} < 0.4: 🟢 低複雜度

---

## 其他指標

| 指標 | 數值 |
|------|------|
| **信心度** | {qmd['confidence']} |
| **數據源數量** | {qmd['source_count']} |

---

## QMD 向量索引

```
QMD = ({qmd['quality']:.2f}, {qmd['maturity']:.2f}, {qmd['difficulty']:.2f})
```

這個三維向量可以用於：
- 相似性搜索（餘弦相似度、歐氏距離）
- 聚類分析（K-means、層次聚類）
- 推薦系統（基於 QMD 的內容推薦）

---

## 建議

### 如果 Quality < 0.6
- 增加標準章節（摘要、理論基礎、實證驗證）
- 添加更多數學公式和推導
- 增加實驗和驗證結果
- 添加代碼範例

### 如果 Maturity < 0.5
- 提供開源實現（GitHub）
- 增加工具和 API 文檔
- 提供部署指南

### 如果 Difficulty > 0.7
- 提供背景知識和前置知識
- 添加教程和逐步指導
- 提供更多解釋和範例
"""

    # 寫入文件
    output_path = output_dir / f"{task_id}-qmd.md"
    output_path.write_text(md_content, encoding='utf-8')

    return output_path

def main():
    """
    主函數：掃描所有研究報告，提取 QMD 指標
    """
    works_dir = Path('/Users/charlie/.openclaw/workspace/kanban/works')
    qmd_dir = Path('/Users/charlie/.openclaw/workspace/knowledge/qmd')
    qmd_dir.mkdir(parents=True, exist_ok=True)

    # 查找所有研究報告
    report_files = list(works_dir.glob('**/*research.md'))

    print(f"找到 {len(report_files)} 個研究報告")
    print("=" * 60)

    qmd_records = []
    for report_file in report_files:
        print(f"處理: {report_file.parent.name}")

        # 提取 QMD 指標
        qmd = extract_qmd_from_report(report_file)

        if qmd:
            # 生成 QMD 記錄
            qmd_record_path = generate_qmd_record(qmd, qmd_dir)
            qmd_records.append(qmd)

            print(f"  Quality: {qmd['quality']:.2f}")
            print(f"  Maturity: {qmd['maturity']:.2f}")
            print(f"  Difficulty: {qmd['difficulty']:.2f}")
            print(f"  QMD: ({qmd['quality']:.2f}, {qmd['maturity']:.2f}, {qmd['difficulty']:.2f})")
            print(f"  信心度: {qmd['confidence']}")
            print(f"  記錄: {qmd_record_path}")
            print()

    # 生成 QMD 索引
    if qmd_records:
        index_path = qmd_dir / 'INDEX.md'

        # 按日期排序
        qmd_records_sorted = sorted(qmd_records, key=lambda x: x['report_path'], reverse=True)

        # 生成索引
        index_content = """# QMD 索引

> **生成時間：** {now}
> **總記錄數：** {count}
> **修正版本：** v2.0（權重標準化）

---

## QMD 統計

### 平均值

| 指標 | 平均值 |
|------|--------|
| **Quality** | {avg_quality:.2f} |
| **Maturity** | {avg_maturity:.2f} |
| **Difficulty** | {avg_difficulty:.2f} |

### 分佈

#### Quality 分佈
- 🟢 優秀 (>= 0.8): {excellent_quality} 個
- 🟡 良好 (0.6-0.8): {good_quality} 個
- 🔴 需要改進 (< 0.6): {poor_quality} 個

#### Maturity 分佈
- 🟢 成熟 (>= 0.7): {mature_tasks} 個
- 🟡 部分成熟 (0.4-0.7): {partial_mature_tasks} 個
- 🔴 早期階段 (< 0.4): {early_stage_tasks} 個

#### Difficulty 分佈
- 🔴 高複雜度 (>= 0.7): {high_difficulty} 個
- 🟡 中等複雜度 (0.4-0.7): {medium_difficulty} 個
- 🟢 低複雜度 (< 0.4): {low_difficulty} 個

---

## 詳細記錄

| 任務 ID | Quality | Maturity | Difficulty | QMD 向量 | 信心度 | 數據源 |
|---------|---------|----------|-----------|----------|--------|--------|
""".format(
            now=datetime.now().isoformat(),
            count=len(qmd_records),
            avg_quality=sum(r['quality'] for r in qmd_records) / len(qmd_records),
            avg_maturity=sum(r['maturity'] for r in qmd_records) / len(qmd_records),
            avg_difficulty=sum(r['difficulty'] for r in qmd_records) / len(qmd_records),
            excellent_quality=sum(1 for r in qmd_records if r['quality'] >= 0.8),
            good_quality=sum(1 for r in qmd_records if 0.6 <= r['quality'] < 0.8),
            poor_quality=sum(1 for r in qmd_records if r['quality'] < 0.6),
            mature_tasks=sum(1 for r in qmd_records if r['maturity'] >= 0.7),
            partial_mature_tasks=sum(1 for r in qmd_records if 0.4 <= r['maturity'] < 0.7),
            early_stage_tasks=sum(1 for r in qmd_records if r['maturity'] < 0.4),
            high_difficulty=sum(1 for r in qmd_records if r['difficulty'] >= 0.7),
            medium_difficulty=sum(1 for r in qmd_records if 0.4 <= r['difficulty'] < 0.7),
            low_difficulty=sum(1 for r in qmd_records if r['difficulty'] < 0.4),
        )

        for qmd in qmd_records_sorted:
            index_content += f"| {qmd['task_id']} | {qmd['quality']:.2f} | {qmd['maturity']:.2f} | {qmd['difficulty']:.2f} | ({qmd['quality']:.2f}, {qmd['maturity']:.2f}, {qmd['difficulty']:.2f}) | {qmd['confidence']} | {qmd['source_count']} |\n"

        # 寫入索引
        index_path.write_text(index_content, encoding='utf-8')

        print("=" * 60)
        print(f"QMD 索引: {index_path}")
        print(f"QMD 記錄: {qmd_dir}")
        print(f"總記錄數: {len(qmd_records)}")
        print()
        print("✅ 權重標準化完成：Quality 現在在 0-1 範圍內")

if __name__ == '__main__':
    main()

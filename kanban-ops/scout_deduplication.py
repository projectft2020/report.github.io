#!/usr/bin/env python3
"""
Scout 去重檢查器

在 Scout 創建任務前，檢查是否已存在相同或相似任務。
避免創建重複的任務。
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from difflib import SequenceMatcher

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_FILE = WORKSPACE / "kanban" / "tasks.json"
QDM_INDEX = WORKSPACE / "scout-ops" / "QDM_INDEX.json"

# 相似度閾值
TITLE_SIMILARITY_THRESHOLD = 0.85  # 85% 相似度


def load_tasks() -> List[Dict]:
    """載入所有任務"""
    if not TASKS_FILE.exists():
        return []

    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_arxiv_id(title: str) -> Optional[str]:
    """從標題中提取 arXiv ID（如果存在）"""
    # 常見格式：arXiv:1234.5678, arXiv ID: 1234.5678, etc.
    patterns = [
        r'arXiv:\s*(\d{4}\.\d{4,5})',
        r'arXiv\s+ID:\s*(\d{4}\.\d{4,5})',
        r'arXiv\s*(\d{4}\.\d{4,5})',
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def load_qdm_index() -> Dict[str, List[str]]:
    """載入 QDM 索引"""
    if not QDM_INDEX.exists():
        return {}

    with open(QDM_INDEX, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_similarity(str1: str, str2: str) -> float:
    """計算兩個字符串的相似度（0.0 - 1.0）"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def check_exact_match(title: str, tasks: List[Dict]) -> Optional[Dict]:
    """檢查是否有完全相同的標題"""
    for task in tasks:
        if task.get('title') == title:
            return task
    return None


def check_arxiv_id(arxiv_id: str, tasks: List[Dict], qdm_index: Dict) -> Optional[Dict]:
    """檢查 arXiv ID 是否已存在"""
    # 檢查 tasks.json
    for task in tasks:
        task_arxiv_id = extract_arxiv_id(task.get('title', ''))
        if task_arxiv_id and task_arxiv_id == arxiv_id:
            return task

    # 檢查 QDM 索引
    if 'arxiv' in qdm_index:
        for topic in qdm_index['arxiv']:
            topic_arxiv_id = extract_arxiv_id(topic.get('title', ''))
            if topic_arxiv_id and topic_arxiv_id == arxiv_id:
                return {'type': 'qdm', 'topic': topic}

    return None


def check_similar_title(title: str, tasks: List[Dict], threshold: float) -> Optional[Dict]:
    """檢查是否有相似的標題"""
    for task in tasks:
        similarity = calculate_similarity(title, task.get('title', ''))
        if similarity >= threshold:
            return {
                'task': task,
                'similarity': similarity
            }
    return None


def check_completed_task(title: str, tasks: List[Dict]) -> Optional[Dict]:
    """檢查是否有相同標題的已完成任務"""
    for task in tasks:
        if task.get('title') == title and task.get('status') == 'completed':
            return task
    return None


def should_create_task(title: str, verbose: bool = True) -> Dict:
    """
    判斷是否應該創建任務（考慮所有去重檢查）

    Args:
        title: 任務標題
        verbose: 是否輸出詳細日誌

    Returns:
        dict: 檢查結果
            - should_create: bool - 是否應該創建
            - reason: str - 原因
            - matched_task: dict - 匹配的任務（如果有）
            - similarity: float - 相似度（如果有）
    """

    # 載入數據
    tasks = load_tasks()
    qdm_index = load_qdm_index()

    # 檢查 1: 完全相同的標題
    exact_match = check_exact_match(title, tasks)
    if exact_match:
        reason = f"標題完全匹配（任務 ID: {exact_match['id']}）"
        if verbose:
            print(f"❌ [去重] {reason}")
        return {
            'should_create': False,
            'reason': reason,
            'matched_task': exact_match
        }

    # 檢查 2: 相同標題的已完成任務
    completed_match = check_completed_task(title, tasks)
    if completed_match:
        reason = f"相同標題的任務已完成（任務 ID: {completed_match['id']}）"
        if verbose:
            print(f"❌ [去重] {reason}")
        return {
            'should_create': False,
            'reason': reason,
            'matched_task': completed_match
        }

    # 檢查 3: arXiv ID 去重
    arxiv_id = extract_arxiv_id(title)
    if arxiv_id:
        arxiv_match = check_arxiv_id(arxiv_id, tasks, qdm_index)
        if arxiv_match:
            if 'task' in arxiv_match:
                reason = f"arXiv ID {arxiv_id} 已存在（任務 ID: {arxiv_match['task']['id']}）"
            else:
                reason = f"arXiv ID {arxiv_id} 已在 QDM 中索引"
            if verbose:
                print(f"❌ [去重] {reason}")
            return {
                'should_create': False,
                'reason': reason,
                'matched_task': arxiv_match.get('task'),
                'arxiv_id': arxiv_id
            }

    # 檢查 4: 標題相似度
    similar_match = check_similar_title(title, tasks, TITLE_SIMILARITY_THRESHOLD)
    if similar_match:
        reason = f"標題相似度 {similar_match['similarity']:.1%} >= {TITLE_SIMILARITY_THRESHOLD:.0%}"
        if verbose:
            print(f"❌ [去重] {reason}")
            print(f"   原標題: {title[:60]}...")
            print(f"   相似標題: {similar_match['task']['title'][:60]}...")
        return {
            'should_create': False,
            'reason': reason,
            'matched_task': similar_match['task'],
            'similarity': similar_match['similarity']
        }

    # 通過所有檢查
    if verbose:
        print(f"✅ [去重] 通過所有檢查，可以創建任務")
    return {
        'should_create': True,
        'reason': '通過所有檢查',
        'matched_task': None
    }


def batch_check_topics(topics: List[Dict], verbose: bool = True) -> List[Dict]:
    """
    批量檢查多個主題

    Args:
        topics: 主題列表（每個主題包含 'title' 字段）
        verbose: 是否輸出詳細日誌

    Returns:
        list: 檢查結果列表
    """
    results = []

    for topic in topics:
        title = topic.get('title', '')
        result = should_create_task(title, verbose)
        result['topic'] = topic
        results.append(result)

    return results


def main():
    """主函數（測試用）"""
    import sys

    if len(sys.argv) < 2:
        print("""
Scout 去重檢查器

用法：
    python3 scout_deduplication.py check "任務標題"
    python3 scout_deduplication.py batch

示例：
    python3 scout_deduplication.py check "From Chain-Ladder to Individual Claims Reserving"
        """)
        sys.exit(0)

    command = sys.argv[1]

    if command == 'check':
        if len(sys.argv) < 3:
            print("錯誤：請提供任務標題")
            sys.exit(1)

        title = ' '.join(sys.argv[2:])
        result = should_create_task(title)

        print(f"\n檢查結果：")
        print(f"  應該創建: {'是' if result['should_create'] else '否'}")
        print(f"  原因: {result['reason']}")
        if result.get('matched_task'):
            print(f"  匹配任務: {result['matched_task']['id']}")
        if result.get('similarity'):
            print(f"  相似度: {result['similarity']:.1%}")

    elif command == 'batch':
        # 測試批量檢查
        test_topics = [
            {"title": "From Chain-Ladder to Individual Claims Reserving"},
            {"title": "A Theoretical Framework for Modular Learning of Robust Generative Models"},
            {"title": "Asymptotically Optimal Sequential Testing with Markovian Data"},
            {"title": "New Research Paper That Doesn't Exist Yet"},
        ]

        print("批量檢查測試：\n")
        results = batch_check_topics(test_topics)

        print("\n檢查結果總結：")
        print(f"  總數: {len(results)}")
        print(f"  可創建: {sum(1 for r in results if r['should_create'])}")
        print(f"  應過濾: {sum(1 for r in results if not r['should_create'])}")

    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

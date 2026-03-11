#!/usr/bin/env python3
"""
QMD Enhanced Input Compressor

智能選擇壓縮方式：
- 小文件（< 30 KB）：基礎壓縮（快速）
- 大文件（>= 30 KB）：QMD 語意搜索（更精準）
- QMD 失敗時自動回退到基礎壓縮
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class QMDEnhancedCompressor:
    """智能輸入壓縮器 - 整合基礎壓縮和 QMD 語意搜索"""

    def __init__(
        self,
        qmd_path: str = "~/.qmd/qmd",
        semantic_threshold: int = 30 * 1024  # 30 KB
    ):
        self.qmd_path = Path(qmd_path).expanduser()
        self.semantic_threshold = semantic_threshold

        # 檢查 QMD 是否可用
        self.qmd_available = self._check_qmd_available()

    def _check_qmd_available(self) -> bool:
        """檢查 QMD 是否可用"""
        try:
            result = subprocess.run(
                [str(self.qmd_path), '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def compress_file(
        self,
        file_path: str,
        task_query: str = "",
        force_method: Optional[str] = None
    ) -> Dict:
        """
        智能壓縮文件

        Args:
            file_path: 文件路徑
            task_query: 任務描述（用於語意搜索）
            force_method: 強制使用指定方法 ('basic' 或 'semantic')

        Returns:
            壓縮結果字典
        """

        path = Path(file_path)

        if not path.exists():
            return {
                'error': f'File not found: {file_path}',
                'file': str(path)
            }

        file_size = path.stat().st_size

        # 決定使用哪種壓縮方法
        if force_method:
            method = force_method
        elif not self.qmd_available:
            method = 'basic'
        elif not task_query:
            # 沒有任務描述，無法做語意搜索
            method = 'basic'
        elif file_size >= self.semantic_threshold:
            # 大文件，使用語意搜索
            method = 'semantic'
        else:
            # 小文件，使用基礎壓縮
            method = 'basic'

        # 執行壓縮
        if method == 'semantic':
            print(f"🧠 Using semantic compression for {path.name} ({file_size//1024}KB)")
            result = self._semantic_compress(file_path, task_query)
        else:
            print(f"⚡ Using basic compression for {path.name} ({file_size//1024}KB)")
            result = self._basic_compress(file_path)

        return result

    def _semantic_compress(self, file_path: str, task_query: str) -> Dict:
        """使用 QMD 語意搜索壓縮"""

        path = Path(file_path)

        # 使用 QMD 向量搜索
        cmd = [
            str(self.qmd_path),
            'vsearch',
            task_query,
            '-c', 'kanban-workspace',
            '-n', '5',
            '--json'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )

            if result.returncode != 0:
                print(f"⚠️  QMD search failed, falling back to basic compression")
                return self._basic_compress(file_path)

            # 解析 QMD JSON 結果
            try:
                qmd_results = json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"⚠️  QMD returned invalid JSON, falling back to basic compression")
                return self._basic_compress(file_path)

            # 提取相關內容
            relevant_content = self._extract_relevant_content(
                qmd_results,
                file_path,
                task_query
            )

            if not relevant_content:
                print(f"⚠️  No relevant content found, falling back to basic compression")
                return self._basic_compress(file_path)

            print(f"✅ Semantic compression: found {len(relevant_content)} relevant sections")

            return {
                'source_file': str(path.name),
                'method': 'qmd_semantic',
                'query': task_query,
                'content': relevant_content,
                'original_size': path.stat().st_size,
                'compressed_size': len(relevant_content.encode('utf-8')),
                'compression_ratio': (1 - len(relevant_content.encode('utf-8')) / path.stat().st_size) * 100
            }

        except subprocess.TimeoutExpired:
            print(f"⚠️  QMD search timeout, falling back to basic compression")
            return self._basic_compress(file_path)
        except Exception as e:
            print(f"⚠️  QMD search error: {e}, falling back to basic compression")
            return self._basic_compress(file_path)

    def _extract_relevant_content(
        self,
        qmd_results: dict,
        file_path: str,
        task_query: str
    ) -> str:
        """從 QMD 結果中提取相關內容"""

        path = Path(file_path)

        # QMD 返回的結果格式是數組
        results = qmd_results if isinstance(qmd_results, list) else qmd_results.get('results', [])

        if not results:
            # 如果沒有結果，讀取整個文件並做基礎提取
            return self._basic_extract_content(path)

        # 收集所有相關的 snippet
        relevant_snippets = []

        for item in results:
            # 檢查是否匹配目標文件
            item_file = item.get('file', '')
            if not self._is_same_file(item_file, str(path)):
                continue

            # 提取相關內容（QMD 返回 snippet 字段）
            snippet = item.get('snippet', '')
            if snippet:
                relevant_snippets.append({
                    'score': item.get('score', 0),
                    'content': snippet
                })

        if not relevant_snippets:
            # 沒有找到相關 snippets，回退到基礎提取
            return self._basic_extract_content(path)

        # 按相關性排序並合併
        relevant_snippets.sort(key=lambda x: x['score'], reverse=True)

        # 取最相關的前 5 個 snippets
        top_snippets = relevant_snippets[:5]

        # 合併內容
        merged_content = "\n\n---\n\n".join([
            snippet['content'] for snippet in top_snippets
        ])

        return merged_content

    def _is_same_file(self, qmd_path: str, actual_path: str) -> bool:
        """檢查 QMD 路徑是否匹配實際文件

        QMD 返回格式: qmd://kanban-workspace/path/to/file.md
        實際路徑格式: /Users/charlie/.openclaw/workspace/path/to/file.md
        """

        # 處理 QMD URL 格式
        if qmd_path.startswith('qmd://'):
            # 從 qmd://kanban-workspace/path/to/file.md 提取 path/to/file.md
            qmd_path = qmd_path.split('kanban-workspace/', 1)[-1] if 'kanban-workspace/' in qmd_path else qmd_path

        qmd = Path(qmd_path).expanduser()
        actual = Path(actual_path).expanduser()

        # 比較文件名
        return qmd.name == actual.name

    def _basic_extract_content(self, path: Path) -> str:
        """基礎內容提取"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取關鍵部分
            sections = []

            # 標題
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                sections.append(f"# {title_match.group(1)}")

            # 主要章節（前 3 個）
            chapter_pattern = r'^##\s+(.+?)$'
            chapters = re.finditer(chapter_pattern, content, re.MULTILINE)
            for i, match in enumerate(chapters):
                if i >= 3:
                    break
                chapter_title = match.group(1)
                # 提取章節內容（最多 500 字）
                chapter_start = match.end()
                next_chapter = re.search(r'^##\s+', content[chapter_start:], re.MULTILINE)
                if next_chapter:
                    chapter_end = chapter_start + next_chapter.start()
                else:
                    chapter_end = len(content)

                chapter_content = content[chapter_start:chapter_end].strip()
                sections.append(f"## {chapter_title}\n\n{chapter_content[:500]}")

            return "\n\n".join(sections)

        except Exception as e:
            return f"Error reading file: {e}"

    def _basic_compress(self, file_path: str) -> Dict:
        """基礎壓縮（提取關鍵信息）"""

        # 導入基礎提取器
        import sys
        sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'kanban-ops'))

        try:
            from input_extractor import extract_key_info
            return extract_key_info(file_path, verbose=False)
        except ImportError:
            # 如果 input_extractor 不可用，使用內建的基礎提取
            return self._basic_compress_fallback(file_path)

    def _basic_compress_fallback(self, file_path: str) -> Dict:
        """基礎壓縮的回退方案"""
        path = Path(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        extracted_content = self._basic_extract_content(path)

        return {
            'source_file': str(path.name),
            'method': 'basic_fallback',
            'title': path.stem,
            'summary': extracted_content[:1000],
            'content': extracted_content,
            'original_size': path.stat().st_size,
            'compressed_size': len(extracted_content.encode('utf-8')),
            'compression_ratio': (1 - len(extracted_content.encode('utf-8')) / path.stat().st_size) * 100
        }


def compress_task_inputs(
    task_id: str,
    tasks_json: Optional[str] = None,
    force_method: Optional[str] = None
) -> Dict:
    """
    壓縮任務的所有輸入文件

    Args:
        task_id: 任務 ID
        tasks_json: tasks.json 路徑（默認：~/.openclaw/workspace-automation/kanban/tasks.json）
        force_method: 強制使用指定方法 ('basic' 或 'semantic')

    Returns:
        壓縮結果統計
    """

    if tasks_json is None:
        tasks_json = str(Path.home() / '.openclaw' / 'workspace-automation' / 'kanban' / 'tasks.json')

    tasks_path = Path(tasks_json)

    if not tasks_path.exists():
        return {
            'error': f'Tasks file not found: {tasks_json}',
            'task_id': task_id
        }

    # 載入任務
    with open(tasks_path, 'r') as f:
        data = json.load(f)

    # 找到目標任務
    task = None
    for t in data.get('tasks', []):
        if t.get('id') == task_id or t['id'].endswith(task_id):
            task = t
            break

    if not task:
        return {
            'error': f'Task not found: {task_id}',
            'task_id': task_id
        }

    # 獲取輸入路徑
    input_paths = task.get('input_paths', [])

    if not input_paths:
        return {
            'message': 'No input paths for this task',
            'task_id': task_id,
            'task_title': task.get('title', ''),
            'total_original': 0,
            'total_compressed': 0,
            'files_compressed': 0
        }

    # 構建任務查詢（用於語意搜索）
    task_query = f"{task.get('title', '')} {task.get('notes', '')} {task.get('description', '')}"

    # 創建壓縮器
    compressor = QMDEnhancedCompressor()

    # 壓縮每個輸入文件
    results = []
    total_original = 0
    total_compressed = 0

    print(f"📦 Compressing {len(input_paths)} input files for task: {task_id}")
    print(f"   Query: {task_query[:100]}...")
    print()

    for input_path in input_paths:
        path = Path(input_path)

        if not path.exists():
            print(f"  ⚠️  File not found: {input_path}")
            continue

        result = compressor.compress_file(
            str(path),
            task_query=task_query,
            force_method=force_method
        )

        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
            continue

        orig = result.get('original_size', 0)
        comp = result.get('compressed_size', 0)
        ratio = result.get('compression_ratio', 0)
        method = result.get('method', 'unknown')

        total_original += orig
        total_compressed += comp

        print(f"  → {path.name}: {orig//1024}KB → {comp//1024}KB ({method}, 節省 {ratio:.1f}%)")

        results.append(result)

    if total_original > 0:
        saved = (1 - total_compressed / total_original) * 100
        print(f"\n✅ Total: {total_original//1024}KB → {total_compressed//1024}KB (節省 {saved:.1f}%)")

    return {
        'task_id': task_id,
        'task_title': task.get('title', ''),
        'files_compressed': len(results),
        'total_original': total_original,
        'total_compressed': total_compressed,
        'overall_compression': (1 - total_compressed / total_original) * 100 if total_original > 0 else 0,
        'results': results
    }


# 命令行界面
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <task_id>                    # 自動選擇最佳方法")
        print(f"  {sys.argv[0]} <task_id> --basic            # 強制使用基礎壓縮")
        print(f"  {sys.argv[0]} <task_id> --semantic         # 強制使用語意搜索")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} dhri001")
        sys.exit(1)

    task_id = sys.argv[1]
    force_method = None

    if len(sys.argv) >= 3:
        if sys.argv[2] == '--basic':
            force_method = 'basic'
        elif sys.argv[2] == '--semantic':
            force_method = 'semantic'

    result = compress_task_inputs(task_id, force_method=force_method)

    if 'error' in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    print(f"\n📊 Summary:")
    print(f"   Task: {result.get('task_title', task_id)}")
    print(f"   Files: {result['files_compressed']}")
    print(f"   Compression: {result['overall_compression']:.1f}%")

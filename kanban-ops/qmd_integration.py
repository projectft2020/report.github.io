#!/usr/bin/env python3
"""
QMD Semantic Input Compressor

使用 QMD 的向量搜索功能進行語義輸入壓縮。
相比基礎壓縮，這可以只提取與任務最相關的部分。
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


class QMDSemanticCompressor:
    """使用 QMD 進行語義壓縮"""

    def __init__(self, qmd_path: str = "~/.qmd/qmd"):
        self.qmd_path = Path(qmd_path).expanduser()

    def retrieve_relevant_content(
        self,
        file_path: str,
        task_query: str,
        max_results: int = 3,
        use_vector: bool = True
    ) -> Dict:
        """
        使用 QMD 檢索與任務最相關的內容

        Args:
            file_path: 輸入文件路徑
            task_query: 任務描述/查詢
            max_results: 最多返回幾個結果
            use_vector: 是否使用向量搜索（vs 關鍵詞搜索）

        Returns:
            壓縮後的內容字典
        """

        path = Path(file_path)

        if not path.exists():
            return {
                'error': f'File not found: {file_path}',
                'file': str(path)
            }

        # 使用 QMD 搜索
        if use_vector:
            # 向量語義搜索（更精確）
            cmd = [
                str(self.qmd_path),
                'vsearch',
                task_query,
                '-c', 'kanban-workspace',  # 在看板 workspace 中搜索
                '-n', str(max_results),
                '--files'  # 只返回文件列表
            ]
            search_type = 'vector'
        else:
            # BM25 關鍵詞搜索（更快）
            cmd = [
                str(self.qmd_path),
                'search',
                task_query,
                '-c', 'kanban-workspace',
                '-n', str(max_results),
                '--files',
                '--min-score', '0.3'  # 最低相關性分數
            ]
            search_type = 'keyword'

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )

            if result.returncode != 0:
                # 如果 QMD 搜索失敗，回退到基礎壓縮
                print(f"⚠️  QMD {search_type} search failed, using basic compression")
                return self._fallback_compress(file_path)

            # 解析 QMD 結果
            files = self._parse_qmd_files(result.stdout)

            if not files:
                # 沒有找到相關文件，回退到基礎壓縮
                print(f"⚠️  No relevant files found, using basic compression")
                return self._fallback_compress(file_path)

            # 獲取最相關的文件內容
            relevant_content = []
            total_size = 0

            for file_info in files[:max_results]:
                file_content = self._get_file_content(file_info['path'])
                if file_content:
                    relevant_content.append({
                        'file': file_info['path'],
                        'score': file_info.get('score', 0),
                        'content': file_content[:2000]  # 限制大小
                    })
                    total_size += len(file_content)

            print(f"✅ QMD {search_type} search: found {len(relevant_content)} relevant sections")

            return {
                'source_file': str(path.name),
                'method': f'qmd_{search_type}',
                'query': task_query,
                'results': relevant_content,
                'original_size': path.stat().st_size,
                'compressed_size': total_size,
                'compression_ratio': (1 - total_size / path.stat().st_size) * 100
            }

        except subprocess.TimeoutExpired:
            print(f"⚠️  QMD search timeout, using basic compression")
            return self._fallback_compress(file_path)
        except Exception as e:
            print(f"⚠️  QMD search error: {e}, using basic compression")
            return self._fallback_compress(file_path)

    def _parse_qmd_files(self, output: str) -> List[Dict]:
        """解析 QMD 輸出的文件列表"""
        files = []

        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '|' in line:
                # 解析文件路徑
                parts = line.split('|')
                if len(parts) >= 1:
                    file_path = parts[0].strip()
                    if file_path:
                        files.append({'path': file_path})

        return files

    def _get_file_content(self, file_path: str) -> str:
        """獲取文件內容"""
        path = Path(file_path)
        if not path.exists():
            return ""

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _fallback_compress(self, file_path: str) -> Dict:
        """回退到基礎壓縮"""
        # 導入基礎壓縮器
        import sys
        sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'kanban-ops'))
        from input_extractor import extract_key_info

        return extract_key_info(file_path, verbose=False)


# 使用示例
if __name__ == '__main__':
    import sys

    compressor = QMDSemanticCompressor()

    # 測試語義壓縮
    task_query = "DHRI calculation formula and hedge ratio lookup table"
    file_path = "/Users/charlie/.openclaw/workspace/DHRI-daily-hedge-ratio.md"

    print(f"🔍 Testing QMD semantic compression")
    print(f"   Query: {task_query}")
    print(f"   File: {file_path}")
    print()

    result = compressor.retrieve_relevant_content(
        file_path=file_path,
        task_query=task_query,
        use_vector=True  # 使用向量搜索
    )

    print(f"\n📦 Results:")
    print(f"   Method: {result.get('method', 'unknown')}")
    print(f"   Original: {result.get('original_size', 0) // 1024}KB")
    print(f"   Compressed: {result.get('compressed_size', 0) // 1024}KB")
    print(f"   Saved: {result.get('compression_ratio', 0):.1f}%")

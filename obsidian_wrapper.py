#!/usr/bin/env python3
"""
Obsidian CLI Python Wrapper

這個包裝器提供了 Obsidian CLI 的 Python 接口，讓我可以完全使用 Obsidian 作為知識管理工具。

使用方式：
    from obsidian_wrapper import ObsidianCLI

    obsidian = ObsidianCLI()
    obsidian.create("test.md", "Hello, World!")
    content = obsidian.read("test.md")
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianCLI:
    """Obsidian CLI 包裝器"""

    def __init__(
        self,
        vault_path: Optional[str] = None,
        obsidian_cmd: Optional[str] = None
    ):
        """
        初始化 Obsidian CLI 包裝器

        參數:
            vault_path: Vault 路徑（默認：/Users/charlie/.openclaw/workspace/quant/research）
            obsidian_cmd: Obsidian CLI 命令路徑（默認：/Applications/Obsidian.app/Contents/MacOS/obsidian）
        """
        self.vault_path = vault_path or "/Users/charlie/.openclaw/workspace/quant/research"
        self.obsidian_cmd = obsidian_cmd or "/Applications/Obsidian.app/Contents/MacOS/obsidian"

        # 驗證 Vault 存在
        if not Path(self.vault_path).exists():
            logger.warning(f"Vault path does not exist: {self.vault_path}")

    def _run_command(
        self,
        cmd: List[str],
        capture_output: bool = False,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        執行 Obsidian CLI 命令

        參數:
            cmd: 命令列表
            capture_output: 是否捕獲輸出
            check: 是否檢查返回碼

        返回:
            subprocess.CompletedProcess
        """
        full_cmd = [self.obsidian_cmd] + cmd

        try:
            result = subprocess.run(
                full_cmd,
                cwd=self.vault_path,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(full_cmd)}")
            logger.error(f"Error: {e.stderr}")
            raise

    def create(
        self,
        name: str,
        content: str,
        path: Optional[str] = None,
        template: Optional[str] = None,
        overwrite: bool = False
    ) -> str:
        """
        創建新筆記

        參數:
            name: 檔案名稱
            content: 初始內容
            path: 路徑（可選）
            template: 模板名稱（可選）
            overwrite: 是否覆蓋已存在的檔案

        返回:
            創建結果訊息
        """
        cmd = [
            "create",
            f"name={name}",
            f'content="{content}"'
        ]

        if path:
            cmd.append(f"path={path}")
        if template:
            cmd.append(f"template={template}")
        if overwrite:
            cmd.append("overwrite")

        self._run_command(cmd)
        logger.info(f"Created note: {name}")
        return f"Created: {name}"

    def read(self, file: str) -> str:
        """
        讀取筆記

        參數:
            file: 檔案名稱

        返回:
            檔案內容
        """
        cmd = ["read", f"file={file}"]
        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def append(
        self,
        file: str,
        content: str,
        inline: bool = False
    ) -> str:
        """
        追加內容到檔案

        參數:
            file: 檔案名稱
            content: 要追加的內容
            inline: 是否不添加換行符

        返回:
            追加結果訊息
        """
        cmd = [
            "append",
            f"file={file}",
            f'content="{content}"'
        ]

        if inline:
            cmd.append("inline")

        self._run_command(cmd)
        logger.info(f"Appended to: {file}")
        return f"Appended to: {file}"

    def prepend(
        self,
        file: str,
        content: str,
        inline: bool = False
    ) -> str:
        """
        在 frontmatter 前添加內容

        參數:
            file: 檔案名稱
            content: 要添加的內容
            inline: 是否不添加換行符

        返回:
            添加結果訊息
        """
        cmd = [
            "prepend",
            f"file={file}",
            f'content="{content}"'
        ]

        if inline:
            cmd.append("inline")

        self._run_command(cmd)
        logger.info(f"Prepended to: {file}")
        return f"Prepended to: {file}"

    def search(
        self,
        query: str,
        limit: int = 10,
        path: Optional[str] = None,
        case_sensitive: bool = False,
        format: str = "json"
    ) -> Union[str, List[str]]:
        """
        搜索 Vault

        參數:
            query: 搜索查詢
            limit: 最大結果數
            path: 限制搜索路徑
            case_sensitive: 是否區分大小寫
            format: 輸出格式（json/text）

        返回:
            搜索結果
        """
        cmd = [
            "search",
            f'query="{query}"',
            f"limit={limit}",
            f"format={format}"
        ]

        if path:
            cmd.append(f"path={path}")
        if case_sensitive:
            cmd.append("case")

        result = self._run_command(cmd, capture_output=True)

        if format == "json":
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    return data
                return []
            except json.JSONDecodeError:
                # 解析輸出（每行一個檔案）
                return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return result.stdout

    def search_context(
        self,
        query: str,
        limit: int = 10,
        path: Optional[str] = None,
        format: str = "json"
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        搜索並顯示上下文

        參數:
            query: 搜索查詢
            limit: 最大結果數
            path: 限制搜索路徑
            format: 輸出格式（json/text）

        返回:
            搜索結果（包含上下文）
        """
        cmd = [
            "search:context",
            f'query="{query}"',
            f"limit={limit}",
            f"format={format}"
        ]

        if path:
            cmd.append(f"path={path}")

        result = self._run_command(cmd, capture_output=True)

        if format == "json":
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
        return result.stdout

    def get_backlinks(
        self,
        file: str,
        counts: bool = False,
        format: str = "json"
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        獲取檔案的反向連結

        參數:
            file: 檔案名稱
            counts: 是否包含連結計數
            format: 輸出格式（json/tsv/csv）

        返回:
            反向連結列表
        """
        cmd = [
            "backlinks",
            f"file={file}",
            f"format={format}"
        ]

        if counts:
            cmd.append("counts")

        result = self._run_command(cmd, capture_output=True)

        if format == "json":
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
        return result.stdout

    def get_links(
        self,
        file: str,
        total: bool = False
    ) -> Union[str, int]:
        """
        獲取檔案的連出連結

        參數:
            file: 檔案名稱
            total: 是否只返回連結數量

        返回:
            連出連結列表或數量
        """
        cmd = ["links", f"file={file}"]

        if total:
            cmd.append("total")
            result = self._run_command(cmd, capture_output=True)
            return int(result.stdout.strip())

        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def get_orphans(self, all_files: bool = False) -> List[str]:
        """
        找出沒有反向連結的檔案

        參數:
            all_files: 是否包含非 markdown 檔案

        返回:
            孤立檔案列表
        """
        cmd = ["orphans"]

        if all_files:
            cmd.append("all")

        result = self._run_command(cmd, capture_output=True)
        # 解析輸出（每行一個檔案）
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

    def get_deadends(self, all_files: bool = False) -> List[str]:
        """
        找出沒有連出連結的檔案

        參數:
            all_files: 是否包含非 markdown 檔案

        返回:
            終端檔案列表
        """
        cmd = ["deadends"]

        if all_files:
            cmd.append("all")

        result = self._run_command(cmd, capture_output=True)
        # 解析輸出（每行一個檔案）
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

    def get_unresolved(self) -> List[str]:
        """
        找出無法解析的連結

        返回:
            無法解析的連結列表
        """
        cmd = ["unresolved", "format=json"]
        result = self._run_command(cmd, capture_output=True)
        # 如果返回 JSON，則解析；否則返回原始輸出
        try:
            data = json.loads(result.stdout)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            # 解析輸出（每行一個連結）
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

    def get_tags(
        self,
        counts: bool = False,
        sort: str = "name",
        format: str = "json"
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        獲取所有標籤

        參數:
            counts: 是否包含計數
            sort: 排序方式（name/count）
            format: 輸出格式（json/tsv/csv）

        返回:
            標籤列表
        """
        cmd = [
            "tags",
            f"format={format}",
            f"sort={sort}"
        ]

        if counts:
            cmd.append("counts")

        result = self._run_command(cmd, capture_output=True)

        if format == "json":
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # 返回空列表
                return []
        return result.stdout

    def daily_open(self, pane_type: str = "tab") -> str:
        """
        打開今日日記

        參數:
            pane_type: 面板類型（tab/split/window）

        返回:
            打開結果訊息
        """
        cmd = ["daily", f"paneType={pane_type}"]
        self._run_command(cmd)
        return "Opened daily note"

    def daily_append(self, content: str, inline: bool = False) -> str:
        """
        追加內容到今日日記

        參數:
            content: 要追加的內容
            inline: 是否不添加換行符

        返回:
            追加結果訊息
        """
        cmd = [
            "daily:append",
            f'content="{content}"'
        ]

        if inline:
            cmd.append("inline")

        self._run_command(cmd)
        logger.info("Appended to daily note")
        return "Appended to daily note"

    def daily_prepend(self, content: str, inline: bool = False) -> str:
        """
        在今日日記的 frontmatter 前添加內容

        參數:
            content: 要添加的內容
            inline: 是否不添加換行符

        返回:
            添加結果訊息
        """
        cmd = [
            "daily:prepend",
            f'content="{content}"'
        ]

        if inline:
            cmd.append("inline")

        self._run_command(cmd)
        logger.info("Prepended to daily note")
        return "Prepended to daily note"

    def daily_read(self) -> str:
        """
        讀取今日日記內容

        返回:
            今日日記內容
        """
        cmd = ["daily:read"]
        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def daily_path(self) -> str:
        """
        獲取今日日記路徑

        返回:
            今日日記路徑
        """
        cmd = ["daily:path"]
        result = self._run_command(cmd, capture_output=True)
        return result.stdout.strip()

    def get_files(
        self,
        folder: Optional[str] = None,
        ext: str = "md",
        total: bool = False
    ) -> Union[str, int]:
        """
        獲取檔案列表

        參數:
            folder: 限制資料夾
            ext: 檔案副檔名
            total: 是否只返回檔案數量

        返回:
            檔案列表或數量
        """
        cmd = ["files", f"ext={ext}"]

        if folder:
            cmd.append(f"folder={folder}")
        if total:
            cmd.append("total")
            result = self._run_command(cmd, capture_output=True)
            return int(result.stdout.strip())

        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def get_folders(
        self,
        folder: Optional[str] = None,
        total: bool = False
    ) -> Union[str, int]:
        """
        獲取資料夾列表

        參數:
            folder: 限制父資料夾
            total: 是否只返回資料夾數量

        返回:
            資料夾列表或數量
        """
        cmd = ["folders"]

        if folder:
            cmd.append(f"folder={folder}")
        if total:
            cmd.append("total")
            result = self._run_command(cmd, capture_output=True)
            return int(result.stdout.strip())

        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def move(self, file: str, to: str) -> str:
        """
        移動或重新命名檔案

        參數:
            file: 檔案名稱
            to: 目標路徑或新名稱

        返回:
            移動結果訊息
        """
        cmd = ["move", f"file={file}", f"to={to}"]
        self._run_command(cmd)
        logger.info(f"Moved {file} to {to}")
        return f"Moved {file} to {to}"

    def rename(self, file: str, name: str) -> str:
        """
        重新命名檔案

        參數:
            file: 檔案名稱
            name: 新名稱

        返回:
            重新命名結果訊息
        """
        cmd = ["rename", f"file={file}", f"name={name}"]
        self._run_command(cmd)
        logger.info(f"Renamed {file} to {name}")
        return f"Renamed {file} to {name}"

    def delete(self, file: str, permanent: bool = False) -> str:
        """
        刪除檔案

        參數:
            file: 檔案名稱
            permanent: 是否永久刪除（不放入回收站）

        返回:
            刪除結果訊息
        """
        cmd = ["delete", f"file={file}"]

        if permanent:
            cmd.append("permanent")

        self._run_command(cmd)
        logger.info(f"Deleted {file}")
        return f"Deleted {file}"

    def eval_js(self, code: str) -> str:
        """
        執行 JavaScript 並返回結果

        參數:
            code: JavaScript 代碼

        返回:
            執行結果
        """
        cmd = ["eval", f'code="{code}"']
        result = self._run_command(cmd, capture_output=True)
        return result.stdout

    def vault_info(self) -> Dict[str, Any]:
        """
        獲取 Vault 資訊

        返回:
            Vault 資訊字典
        """
        cmd = ["vault", "format=json"]
        result = self._run_command(cmd, capture_output=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # 返回空字典
            return {}

    def list_vaults(self) -> List[Dict[str, Any]]:
        """
        列出所有 Vaults

        返回:
            Vaults 列表
        """
        cmd = ["vaults", "format=json"]
        result = self._run_command(cmd, capture_output=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # 返回空列表
            return []


# 便捷函數
def get_obsidian() -> ObsidianCLI:
    """
    獲取預設的 Obsidian CLI 實例

    返回:
        ObsidianCLI 實例
    """
    return ObsidianCLI()

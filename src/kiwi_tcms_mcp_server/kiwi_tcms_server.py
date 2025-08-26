from tcms_api import TCMS
from dotenv import load_dotenv
import os
import ssl
import urllib3
from typing import Any, LiteralString, Optional, Annotated
from datetime import datetime
from fastmcp import FastMCP
from pydantic import BaseModel, Field


# SSL証明書の警告を無効化（開発環境用）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


url = os.environ["TCMS_URL"]
username = os.environ["TCMS_USER"]
password = os.environ["TCMS_PASSWORD"]

# SSL証明書の検証を無効化する（開発環境用）
# 環境変数でSSL検証をコントロール
verify_ssl = os.environ.get("TCMS_VERIFY_SSL", "false").lower() == "true"
if not verify_ssl:
    # SSL証明書の検証を無効化
    ssl._create_default_https_context = ssl._create_unverified_context

rpc = TCMS(url, username, password).exec

# MCPサーバーの初期化
mcp = FastMCP("kiwi-tcms-server")


class Category(BaseModel):
    """テストケースのカテゴリを表現するモデル"""

    id: int = Field(description="categoryのid")
    name: str = Field(description="categoryの名前")
    product: int = Field(description="対象の製品id")
    description: str = Field(description="categoryの説明")


class Priority(BaseModel):
    """テストケースの優先度を表現するモデル"""

    id: int = Field(description="priorityのid")
    value: str = Field(description="優先度の値（P1, P2, P3など）")
    is_active: bool = Field(description="有効かどうか")


class TestCaseStatus(BaseModel):
    """テストケースのステータスを表現するモデル"""

    id: int = Field(description="statusのid")
    name: str = Field(description="statusの名前")
    description: str = Field(description="statusの説明")
    is_confirmed: bool = Field(description="確認済みかどうか")


class TestCase(BaseModel):
    """テストケースを表現するモデル"""

    id: int = Field(description="テストケースのid")
    create_date: Any = Field(description="作成日時")  # DateTime object from API
    is_automated: bool = Field(description="自動化されているか")
    script: str = Field(description="自動化スクリプト")
    arguments: str = Field(description="引数")
    extra_link: Optional[str] = Field(description="追加リンク", default=None)
    summary: str = Field(description="テストケースのサマリー")
    requirement: Optional[str] = Field(description="要件", default=None)
    notes: str = Field(description="メモ")
    text: str = Field(description="テストケースの詳細")
    case_status: int = Field(description="ステータスのid")
    case_status__name: Optional[str] = Field(description="ステータス名", default=None)
    category: int = Field(description="カテゴリのid")
    category__name: Optional[str] = Field(description="カテゴリ名", default=None)
    priority: int = Field(description="優先度のid")
    priority__value: Optional[str] = Field(description="優先度の値", default=None)
    author: int = Field(description="作成者のid")
    author__username: Optional[str] = Field(description="作成者のユーザー名", default=None)
    default_tester: Optional[int] = Field(
        description="デフォルトテスターのid", default=None
    )
    default_tester__username: Optional[str] = Field(
        description="デフォルトテスターのユーザー名", default=None
    )
    reviewer: Optional[int] = Field(description="レビュアーのid", default=None)
    reviewer__username: Optional[str] = Field(
        description="レビュアーのユーザー名", default=None
    )
    setup_duration: Optional[float | str] = Field(
        description="セットアップ時間", default=None
    )
    testing_duration: Optional[float | str] = Field(
        description="テスト実行時間", default=None
    )
    expected_duration: Optional[float] = Field(description="予想時間", default=None)


class TestPlan(BaseModel):
    """テスト計画を表現するモデル"""

    id: int = Field(description="テスト計画のid")
    name: str = Field(description="テスト計画の名前")
    text: str = Field(description="テスト計画の説明")
    create_date: Any = Field(description="作成日時")  # DateTime object from API
    is_active: bool = Field(description="有効かどうか")
    extra_link: Optional[str] = Field(description="追加リンク", default=None)
    product_version: int = Field(description="製品バージョンのid")
    product_version__value: str = Field(description="製品バージョン")
    product: int = Field(description="製品のid")
    product__name: str = Field(description="製品名")
    author: int = Field(description="作成者のid")
    author__username: str = Field(description="作成者のユーザー名")
    type: int = Field(description="タイプのid")
    type__name: str = Field(description="タイプ名")
    parent: Optional[int] = Field(description="親テスト計画のid", default=None)
    children__count: int = Field(description="子テスト計画の数")


@mcp.tool()
def get_categories() -> list[Category]:
    """テストケースのカテゴリの一覧を取得する"""
    res_categories: list[dict[str, Any]] = rpc.Category.filter({})  # type: ignore
    print(f"{type(res_categories)=}")
    categories = [Category(**item_dict) for item_dict in res_categories]
    return categories


@mcp.tool()
def get_priorities() -> list[Priority]:
    """テストケースの優先度の一覧を取得する"""
    res_priorities: list[dict[str, Any]] = rpc.Priority.filter({})  # type: ignore
    print(f"{type(res_priorities)=}")
    priorities = [Priority(**item_dict) for item_dict in res_priorities]
    return priorities


@mcp.tool()
def get_testcase_statuses() -> list[TestCaseStatus]:
    """テストケースのステータスの一覧を取得する"""
    res_statuses: list[dict[str, Any]] = rpc.TestCaseStatus.filter({})  # type: ignore
    print(f"{type(res_statuses)=}")
    statuses = [TestCaseStatus(**item_dict) for item_dict in res_statuses]
    return statuses


@mcp.tool()
def get_testcases() -> list[TestCase]:
    """テストケースの一覧を取得する"""
    res_test_cases: list[dict[str, Any]] = rpc.TestCase.filter({})  # type: ignore
    print(f"{type(res_test_cases)=}")
    test_cases = [TestCase(**item_dict) for item_dict in res_test_cases]
    return test_cases


@mcp.tool()
def create_testcase(
    summary: Annotated[str, Field(description="テストケースのサマリー（タイトル) ")],
    text: Annotated[str, Field(description="テストケースの詳細")],
    category: int = Field(description="カテゴリのid"),
    priority: int = Field(description="優先度のid"),
    case_status: int = Field(description="ステータスのid"),
) -> TestCase:
    """テストケースを新規作成する"""
    value = {
        "summary": summary,
        "text": text,
        "category": category,
        "priority": priority,
        "case_status": case_status,
    }
    res: dict[str: Any] = rpc.TestCase.create(value) # type: ignore
    return TestCase(**res)


@mcp.tool()
def get_testplans() -> list[TestPlan]:
    """テスト計画の一覧を取得する"""
    res_test_plans: list[dict[str, Any]] = rpc.TestPlan.filter({})  # type: ignore
    print(f"{type(res_test_plans)=}")
    test_plans = [TestPlan(**item_dict) for item_dict in res_test_plans]
    return test_plans


def runserver():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp.run(transport="stdio")

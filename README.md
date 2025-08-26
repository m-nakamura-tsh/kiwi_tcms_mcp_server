# 利用方法
実行ディレクトリに `.env` ファイルを作成し、下記の環境変数を設定する。

* `TCMS_URL` : kiwi tcms の xml-rpc エンドポイント。ローカルの docker compose で利用している場合は、 `https://localhost/xml-rpc/` になる
* `TCMS_USER` : kiwi tcms のログインユーザー名
* `TCMS_PASSWORD` : kiw_tcms のログインパスワード
* `TCMS_VERIFY_SSL` : SSL証明書検証を行うかどうか（開発環境はfalse）

**注意**: 本番環境では必ず`TCMS_VERIFY_SSL=true`に設定し、適切な証明書を使用してください。

パッケージがインストールされた状態で、以下を実行する。

```
uv run runserver
```

uvx でも実行可能

```
uvx --from https://github.com/m-nakamura-tsh/kiwi_tcms_mcp_server.git runserver
```

`.env` で環境変数を指定している場合は、以下のコマンドで実行できる


```
 env $(cat .env | xargs) uvx --from https://github.com/m-nakamura-tsh/kiwi_tcms_mcp_server.git runserver
```

# Kiwi TCMS の XML-RPC から操作できるオブジェクトとメソッドについて

## 概要
Kiwi TCMS のAPIをPythonから利用するためのサンプルスクリプトと、利用可能なAPIオブジェクト・メソッドの詳細情報です。


## 利用可能なAPIオブジェクトとメソッド

### 前提知識

kiwi_tcms では、`django-modern-rpc` というモジュールでrpc serverが実装されている。
`@rpc_method` というデコレーターでRPCのメソッドを定義できる。

参考：
[Procedures registration — django-modern-rpc](https://django-modern-rpc.readthedocs.io/latest/basics/register_procedure.html)

実際に実装しているソースはこの辺り。
[Kiwi/tcms/rpc/api/testcase.py at master · kiwitcms/Kiwi](https://github.com/kiwitcms/Kiwi/blob/master/tcms/rpc/api/testcase.py)


以下の例では、rpcのメソッド名は `TestCase.create` として公開されることがわかる。
values を使ってFormをインスタンス化し、`.is_valid()` しているので、Form とその背後の Model によって必須フィールドが定義されている。

```python
@permissions_required("testcases.add_testcase")
@rpc_method(name="TestCase.create")
def create(values, **kwargs):
    """
    .. function:: RPC TestCase.create(values)

        Create a new TestCase object and store it in the database.

        :param values: Field values for :class:`tcms.testcases.models.TestCase`
        :type values: dict
        :param \\**kwargs: Dict providing access to the current request, protocol,
                entry point name and handler instance from the rpc method
        :return: Serialized :class:`tcms.testcases.models.TestCase` object
        :rtype: dict
        :raises ValueError: if form is not valid
        :raises PermissionDenied: if missing *testcases.add_testcase* permission

        Minimal test case parameters::

            >>> values = {
                'category': 135,
                'product': 61,
            'summary': 'Testing XML-RPC',
            'priority': 1,
            }
            >>> TestCase.create(values)
    """
    request = kwargs.get(REQUEST_KEY)

    if not (values.get("author") or values.get("author_id")):
        values["author"] = request.user.pk

    form = NewForm(values)

    if form.is_valid():
        ...

```

### TestPlan - テストプラン管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | テストプランを検索 | `{"is_active": True}` |
| `create(values)` | 新規テストプラン作成 | `{"name": "プラン名", "product": product_id, "type": type_id}` |
| `update(plan_id, values)` | テストプラン更新 | `plan_id, {"name": "新しい名前"}` |
| `add_case(plan_id, case_id)` | テストケース追加 | `plan_id, case_id` |
| `remove_case(plan_id, case_id)` | テストケース削除 | `plan_id, case_id` |
| `add_tag(plan_id, tag_name)` | タグ追加 | `plan_id, "タグ名"` |
| `remove_tag(plan_id, tag_name)` | タグ削除 | `plan_id, "タグ名"` |
| `update_case_order(plan_id, case_id, sortkey)` | ケースの順序変更 | `plan_id, case_id, 100` |
| `list_attachments(plan_id)` | 添付ファイル一覧取得 | `plan_id` |
| `add_attachment(plan_id, filename, b64content)` | 添付ファイル追加 | `plan_id, "file.txt", base64_content` |
| `tree(plan_id)` | プランツリー取得 | `plan_id` |

### TestCase - テストケース管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | テストケース検索 | `{"plan": plan_id}` |
| `create(values)` | 新規テストケース作成 | `{"summary": "概要", "category": cat_id, "priority": pri_id}` |
| `update(case_id, values)` | テストケース更新 | `case_id, {"summary": "新しい概要"}` |
| `remove(query)` | テストケース削除 | `{"id__in": [case_id1, case_id2]}` |
| `history(case_id, query)` | 変更履歴取得 | `case_id` |
| `sortkeys(query)` | ソートキー取得 | `{"plan": plan_id}` |
| `add_component(case_id, component)` | コンポーネント追加 | `case_id, component_name` |
| `remove_component(case_id, component_id)` | コンポーネント削除 | `case_id, component_id` |
| `add_tag(case_id, tag)` | タグ追加 | `case_id, "タグ名"` |
| `remove_tag(case_id, tag)` | タグ削除 | `case_id, "タグ名"` |
| `add_notification_cc(case_id, cc_list)` | CC追加 | `case_id, ["email@example.com"]` |
| `remove_notification_cc(case_id, cc_list)` | CC削除 | `case_id, ["email@example.com"]` |
| `get_notification_cc(case_id)` | CC一覧取得 | `case_id` |
| `list_attachments(case_id)` | 添付ファイル一覧 | `case_id` |
| `add_attachment(case_id, filename, b64content)` | 添付ファイル追加 | `case_id, "file.txt", base64_content` |
| `add_comment(case_id, comment)` | コメント追加 | `case_id, "コメント内容"` |
| `remove_comment(case_id, comment_id)` | コメント削除 | `case_id, comment_id` |
| `comments(case_id)` | コメント一覧取得 | `case_id` |
| `properties(query)` | プロパティ取得 | `{"case": case_id}` |
| `add_property(case_id, name, value)` | プロパティ追加 | `case_id, "key", "value"` |
| `remove_property(query)` | プロパティ削除 | `{"case": case_id, "name": "key"}` |

### TestRun - テストラン管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | テストラン検索 | `{"plan": plan_id}` |
| `create(values)` | 新規テストラン作成 | `{"summary": "ラン名", "manager": user_id, "plan": plan_id}` |
| `update(run_id, values)` | テストラン更新 | `run_id, {"summary": "新しい名前"}` |
| `remove(query)` | テストラン削除 | `{"id": run_id}` |
| `add_case(run_id, case_id)` | テストケース追加 | `run_id, case_id` |
| `remove_case(run_id, case_id)` | テストケース削除 | `run_id, case_id` |
| `get_cases(run_id)` | テストケース一覧取得 | `run_id` |
| `add_tag(run_id, tag_name)` | タグ追加 | `run_id, "タグ名"` |
| `remove_tag(run_id, tag_name)` | タグ削除 | `run_id, "タグ名"` |
| `add_cc(run_id, username)` | CC追加 | `run_id, "username"` |
| `remove_cc(run_id, username)` | CC削除 | `run_id, "username"` |
| `properties(query)` | プロパティ取得 | `{"run": run_id}` |
| `add_attachment(run_id, filename, b64content)` | 添付ファイル追加 | `run_id, "file.txt", base64_content` |

### TestExecution - テスト実行管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | テスト実行検索 | `{"run": run_id}` |
| `update(execution_id, values)` | テスト実行更新 | `execution_id, {"status": status_id}` |
| `remove(query)` | テスト実行削除 | `{"id": execution_id}` |
| `history(execution_id)` | 変更履歴取得 | `execution_id` |
| `add_comment(execution_id, comment)` | コメント追加 | `execution_id, "コメント"` |
| `remove_comment(execution_id, comment_id)` | コメント削除 | `execution_id, comment_id` |
| `get_comments(execution_id)` | コメント一覧取得 | `execution_id` |
| `add_link(values, update_tracker)` | リンク追加 | `{"execution": exec_id, "url": "http://..."}` |
| `remove_link(query)` | リンク削除 | `{"execution": exec_id}` |
| `get_links(query)` | リンク一覧取得 | `{"execution": exec_id}` |
| `properties(query)` | プロパティ取得 | `{"execution": exec_id}` |

### Bug - バグ管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `details(url)` | バグ詳細取得 | `"http://bugtracker/123"` |
| `report(execution_id, tracker_id)` | バグ報告 | `execution_id, tracker_id` |

### Product - プロダクト管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | プロダクト検索 | `{}` |
| `create(values)` | 新規プロダクト作成 | `{"name": "製品名", "classification": class_id}` |

### Version - バージョン管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | バージョン検索 | `{"product": product_id}` |
| `create(values)` | 新規バージョン作成 | `{"value": "1.0", "product": product_id}` |

### Build - ビルド管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | ビルド検索 | `{"version": version_id}` |
| `create(values)` | 新規ビルド作成 | `{"name": "build-001", "version": version_id}` |
| `update(build_id, values)` | ビルド更新 | `build_id, {"is_active": False}` |

### Category - カテゴリー管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | カテゴリー検索 | `{"product": product_id}` |
| `create(values)` | 新規カテゴリー作成 | `{"name": "カテゴリー名", "product": product_id}` |

### Component - コンポーネント管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | コンポーネント検索 | `{"product": product_id}` |
| `create(values)` | 新規コンポーネント作成 | `{"name": "コンポーネント名", "product": product_id}` |
| `update(component_id, values)` | コンポーネント更新 | `component_id, {"name": "新しい名前"}` |

### Tag - タグ管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | タグ検索 | `{}` |

### User - ユーザー管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | ユーザー検索 | `{"username": "user1"}` |
| `update(user_id, values)` | ユーザー情報更新 | `user_id, {"email": "new@example.com"}` |
| `join_group(username, groupname)` | グループ追加 | `"user1", "group1"` |
| `add_attachment(filename, b64content)` | プロフィール画像追加 | `"avatar.png", base64_content` |

### Environment - 環境管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | 環境検索 | `{}` |
| `create(values)` | 新規環境作成 | `{"name": "環境名", "description": "説明"}` |
| `properties(query)` | プロパティ取得 | `{"environment": env_id}` |
| `add_property(environment_id, name, value)` | プロパティ追加 | `env_id, "key", "value"` |
| `remove_property(query)` | プロパティ削除 | `{"environment": env_id, "name": "key"}` |

### Priority - 優先度管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | 優先度検索 | `{"is_active": True}` |

### Classification - 分類管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | 分類検索 | `{}` |
| `create(values)` | 新規分類作成 | `{"name": "分類名"}` |

### PlanType - テストプランタイプ
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | プランタイプ検索 | `{}` |
| `create(values)` | 新規プランタイプ作成 | `{"name": "タイプ名"}` |

### TestCaseStatus - テストケースステータス
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | ステータス検索 | `{"is_confirmed": True}` |

### TestExecutionStatus - テスト実行ステータス
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `filter(query)` | ステータス検索 | `{}` |

### 特殊なオブジェクト

#### KiwiTCMS - システム情報
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `version()` | バージョン取得 | なし |

#### Auth - 認証
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `login(username, password)` | ログイン | `"user", "pass"` |
| `logout()` | ログアウト | なし |

#### Markdown - Markdown処理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `render(text)` | MarkdownをHTMLに変換 | `"**bold text**"` |

#### Attachment - 添付ファイル管理
| メソッド | 説明 | パラメータ例 |
|---------|------|-------------|
| `remove_attachment(attachment_id)` | 添付ファイル削除 | `attachment_id` |

## 使用例

### テストプランの操作
```python
# すべてのテストプランを取得
test_plans = rpc.TestPlan.filter({})

# 新しいテストプランを作成
new_plan = rpc.TestPlan.create({
    "name": "新規テストプラン",
    "product": 1,
    "type": 1,
    "text": "テストプランの説明"
})

# テストケースを追加
rpc.TestPlan.add_case(new_plan["id"], case_id)
```

### テストランの実行
```python
# テストランを作成
test_run = rpc.TestRun.create({
    "summary": "リリース1.0テスト",
    "manager": user_id,
    "plan": plan_id,
    "build": build_id
})

# テスト実行結果を更新
executions = rpc.TestExecution.filter({"run": test_run["id"]})
for execution in executions:
    rpc.TestExecution.update(execution["id"], {
        "status": 4,  # PASSED
        "tested_by": user_id
    })
```

### バグ報告との連携
```python
# テスト実行にバグリンクを追加
rpc.TestExecution.add_link({
    "execution": execution_id,
    "url": "https://bugtracker.example.com/bug/123",
    "name": "Bug #123"
})
```

## スクリプト一覧

- `kiwi_tcms_server.py` - kiwi_tcms の rpc 各種メソッドをwrapした、mcpサーバー 

## 参考資料
- [Kiwi TCMS Documentation](https://kiwitcms.readthedocs.io/)
- [tcms-api Python Package](https://github.com/kiwitcms/tcms-api)
- [Kiwi TCMS XML-RPC API](https://kiwitcms.readthedocs.io/en/latest/modules/tcms.rpc.api.html)

## kiwi_tcmsサーバーの起動

以下コマンドで、stdio モードにて起動する。
```
uv run python kiwi_tcms_server.py
```

### tools などの確認方法

[modelcontextprotocol/inspector: Visual testing tool for MCP servers](https://github.com/modelcontextprotocol/inspector) を利用すると、どのようなtoolsが公開されているかを確認できる。
Webインタフェースがあるので便利。

以下コマンドでWebインタフェースが起動する。

```
npx @modelcontextprotocol/inspector uv run python kiwi_tcms_server.py
```

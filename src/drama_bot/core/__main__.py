"""Local operator CLI: python -m drama_bot.core --help (no paid execution)."""
import argparse
import json
from pathlib import Path

from drama_bot.config import Settings
from drama_bot.contracts import Identity

from .service import CoreService, CreationRequest, PatchRequest


def main():
    parser = argparse.ArgumentParser(description="结构化剧情工程管理；不自动理解自由文本、不调用付费模型")
    parser.add_argument("command", choices=["create", "show", "patch", "job", "retry", "reconcile"])
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--chat", required=True)
    parser.add_argument("--message", default="local-cli")
    parser.add_argument("--id")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--provider-task-id")
    args = parser.parse_args()
    settings = Settings()
    service = CoreService(settings.database_url, settings.allowed_user_ids,
                          settings.allowed_tenant_ids, settings.asset_root)
    who = Identity(tenant_id=args.tenant, user_id=args.user, chat_id=args.chat, message_id=args.message)
    if args.command in {"create", "patch"} and not args.json:
        parser.error("需 --json 结构化请求；自然语言规划器未配置，请人工确认分镜")
    if args.command != "create" and not args.id:
        parser.error("需 --id")
    if args.command == "create":
        result = service.create_project(who, CreationRequest.model_validate_json(args.json.read_text()))
    elif args.command == "patch":
        result = service.patch_version(who, args.id, PatchRequest.model_validate_json(args.json.read_text()))
    elif args.command == "show":
        result = service.get_project(who, args.id)
    elif args.command == "job":
        result = service.get_job(who, args.id)
    elif args.command == "retry":
        result = service.retry_job(who, args.id)
    else:
        result = service.reconcile_submission(who, args.id, args.provider_task_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from models.schemas import ToolDefinition
DESTRUCTIVE_COMMAND_PATTERNS = [
# ==================== FILESYSTEM ====================
"remove-item",
"remove-itemproperty",
"remove-item",
"rm ",
"rmdir",
"rd ",
"del ",
"erase ",
"shred ",
"srm ",
"unlink ",
"wipe ",
"format-",
"format ",
"clear-disk",
"clear-partition",
"diskpart",
"cipher /w",
"robocopy /mir",
"robocopy /purge",
"takeown ",
"icacls ",
"set-acl",

# ==================== POWERSHELL / CMD ====================
"clear-content",
"clear-recyclebin",
"set-content",
"out-file",
"move-item",
"rename-item",
"stop-process",
"taskkill ",
"reg delete",
"reg add",
"bcdedit",
"shutdown ",
"restart-computer",
"stop-computer",

# ==================== LINUX / UNIX ====================
"sudo rm",
"rm -rf",
"rm -r",
"find ",
"-delete",
"dd if=",
"mkfs",
"fdisk",
"parted",
"mount ",
"umount ",
"chmod ",
"chown ",
"chgrp ",
"kill -9",
"killall ",
"pkill ",
"systemctl disable",
"systemctl stop",
"systemctl mask",

# ==================== GIT ====================
"git reset --hard",
"git push --force",
"git push -f",
"git clean -f",
"git clean -fd",
"git clean -fx",
"git checkout --",
"git restore",
"git branch -d",
"git branch -D",
"git branch -M",
"git tag -d",
"git stash drop",
"git stash clear",
"git reflog expire",
"git gc --prune=now",
"git filter-repo",
"git filter-branch",

# ==================== PYTHON ====================
"pip uninstall",
"pip cache purge",
"uv uninstall",
"uv cache clean",
"conda remove",
"conda uninstall",
"python -c",
"python -m shutil",
"venv --clear",

# ==================== NODE.JS ====================
"npm uninstall",
"npm unpublish",
"npm cache clean",
"pnpm remove",
"pnpm uninstall",
"yarn remove",
"yarn cache clean",
"npx rimraf",
"rimraf ",

# ==================== DATABASE ====================
"drop database",
"drop table",
"drop schema",
"drop index",
"drop collection",
"truncate table",
"truncate ",
"delete from",
"alter table",
"alter database",
"delete database",
"db.dropdatabase",
"db.dropexecution",
"db.dropcollection",
"mongosh --eval",

# ==================== DOCKER ====================
"docker rm",
"docker rmi",
"docker system prune",
"docker volume rm",
"docker volume prune",
"docker container prune",
"docker image prune",
"docker network rm",
"docker compose down",
"docker compose down -v",
"docker kill",
"docker stop",

# ==================== KUBERNETES ====================
"kubectl delete",
"kubectl drain",
"kubectl cordon",
"helm uninstall",
"helm delete",

# ==================== TERRAFORM / INFRASTRUCTURE ====================
"terraform destroy",
"terraform apply",
"terraform state rm",
"terraform force-unlock",
"pulumi destroy",
"pulumi cancel",
"ansible-playbook",
"cloudformation delete-stack",

# ==================== AWS ====================
"aws s3 rm",
"aws s3 rb",
"aws ec2 terminate-instances",
"aws ec2 delete-",
"aws rds delete-",
"aws dynamodb delete-table",
"aws lambda delete-function",
"aws iam delete-",
"aws secretsmanager delete-secret",
"aws cloudformation delete-stack",

# ==================== AZURE ====================
"az group delete",
"az vm delete",
"az storage account delete",
"az sql db delete",
"az resource delete",

# ==================== SERVICES / SYSTEM ====================
"sc delete",
"sc stop",
"net stop",
"net user",
"net localgroup",
"systemctl disable",
"systemctl stop",
"service stop",
"launchctl unload",

# ==================== NETWORK / SECURITY ====================
"netsh advfirewall",
"ufw disable",
"ufw delete",
"iptables -f",
"iptables -d",
"firewall-cmd --remove",
"route delete",
"ip route del",

# ==================== REGISTRY / ENVIRONMENT ====================
"remove-item env:",
"setx ",
"reg delete",
"reg import",
"set-executionpolicy",

]

# not meant for security but for confirmation and check, this method allow chat loop to requestion[in voice] to user wheter danger-causing prompt is his explicit choice or not
def requires_confirmation(
    tool_definition: ToolDefinition,
    arguments: dict,
) -> bool:
    if not tool_definition.requires_confirmation:
        return False

    command = arguments.get("command", "")

    return is_destructive_command(command)

def is_destructive_command(command: str) -> bool:
    normalized_command = command.lower().strip()

    return any(
        pattern in normalized_command
        for pattern in DESTRUCTIVE_COMMAND_PATTERNS
    )
# silicon-agents 项目安全规范


## 数据保护
- 执行 `rm`、`del`、`mv`、`rmdir`、`rd`、`erase` 等删除/移动命令前，务必二次确认目标路径是否正确
- 不要覆盖现有文件（尤其是 `.v`、`xml`、`xlsx`、`py` 等设计文件），除非用户明确说"覆盖"或"替换"
- 谨慎使用 `>` 重定向，防止意外覆盖重要文件

## 安全钩子拦截后的处理
- Shell 命令被 PreToolUse hook 拦截时，**禁止用 Python 脚本绕过**
- 必须立即停止操作，向用户说明情况并等待确认

## 不可逆操作
- 对于 `git reset --hard`、`git clean -fd`、`reg delete` 等不可逆操作，必须额外谨慎，一律询问确认

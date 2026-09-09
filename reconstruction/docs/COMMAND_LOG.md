# 工作指令與執行記錄

使用者：開始執行工作表；在檢查關口提出模型疑慮、可能錯誤位置與改善方案；寫指令過程均備份 GitHub。

2026-09-09：唯讀檢查桌面工作模型、現有 repo remote 與 GitHub 權限。確定備份目標 devteam-del/civic；舊本機 remote intern824/civic 未更改。建立 reconstruction/stage-00-scope-audit 分支。

新增 scripts/audit_scope.py、工作表、關卡A問題表、地下來源表；保存前一版腳本 archive。先提交這批指令，再执行audit_scope。此階段不修改 Blender 幾何。

待執行命令（路徑以使用者本地來源參數代入）：

```sh
python3 reconstruction/scripts/audit_scope.py --model-root MODEL_FOLDER --corridor CORRIDOR_GEOJSON --output reconstruction/reports
```

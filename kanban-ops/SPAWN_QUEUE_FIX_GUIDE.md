# Spawn Queue 死锁修复方案

## 架构改进

### 当前流程（有缺陷）
```
1. Task Runner 标记任务为 in_progress
2. 调用 sessions_spawn
3. [缺失] 验证子代理是否启动成功
4. [缺失] 失败时回滚状态
```

### 改进后流程
```
1. Task Runner 标记任务为 spawning （新增状态）
2. 调用 sessions_spawn
3. 等待 5 秒
4. 验证子代理启动：
   - 检查 childSessionKey 是否存在
   - 检查 .status 文件是否生成
   - 调用 sessions_history 验证运行
5. 启动成功：spawning → in_progress
6. 启动失败：spawning → pending（回滚）+ 记录错误
```

## 实现建议

### A. 添加新任务状态
```javascript
// 任务状态机
const TASK_STATES = {
  pending: 'pending',
  spawning: 'spawning',    // 新增：正在启动子代理
  in_progress: 'in_progress',
  completed: 'completed',
  failed: 'failed'
}
```

### B. 子代理启动验证函数
```javascript
async function verifySubagentStartup(sessionKey, childSessionKey, timeout = 10000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    // 1. 检查 childSessionKey
    const history = await sessions_history({ 
      sessionKey: childSessionKey,
      limit: 1 
    });
    
    if (history && history.length > 0) {
      // 2. 检查 .status 文件
      const statusPath = `~/.openclaw/agents/${agentId}/sessions/${childSessionKey}/.status`;
      const statusExists = await fileExists(statusPath);
      
      if (statusExists) {
        return { success: true };
      }
    }
    
    await sleep(1000); // 每秒检查一次
  }
  
  return { 
    success: false, 
    error: 'Subagent failed to start within timeout' 
  };
}
```

### C. 修改 Task Runner
```javascript
async function executeTask(task) {
  try {
    // 1. 更新状态为 spawning
    await updateTaskStatus(task.id, 'spawning');
    
    // 2. 调用 sessions_spawn
    const spawnResult = await sessions_spawn({
      sessionKey: mainSessionKey,
      agentId: task.agentId,
      message: task.prompt
    });
    
    if (!spawnResult.childSessionKey) {
      throw new Error('sessions_spawn failed: no childSessionKey');
    }
    
    // 3. 验证子代理启动
    const verification = await verifySubagentStartup(
      mainSessionKey, 
      spawnResult.childSessionKey,
      10000 // 10秒超时
    );
    
    if (!verification.success) {
      throw new Error(verification.error);
    }
    
    // 4. 启动成功，更新为 in_progress
    await updateTaskStatus(task.id, 'in_progress', {
      childSessionKey: spawnResult.childSessionKey,
      startedAt: new Date().toISOString()
    });
    
  } catch (error) {
    // 5. 失败回滚
    await updateTaskStatus(task.id, 'pending', {
      lastError: error.message,
      retryCount: (task.retryCount || 0) + 1
    });
    
    console.error(`Task ${task.id} spawn failed:`, error);
  }
}
```

### D. 添加重试机制
```javascript
async function shouldRetryTask(task) {
  const MAX_RETRIES = 2;
  const RETRY_DELAY = 60000; // 1分钟
  
  if (task.retryCount >= MAX_RETRIES) {
    await updateTaskStatus(task.id, 'failed', {
      reason: 'Max retries exceeded'
    });
    return false;
  }
  
  const lastAttempt = new Date(task.lastAttemptAt);
  const now = new Date();
  
  if (now - lastAttempt < RETRY_DELAY) {
    return false; // 还没到重试时间
  }
  
  return true;
}
```

## 清理脚本

### 清理当前被阻塞的任务
```bash
#!/bin/bash
# cleanup-stuck-tasks.sh

TASK_IDS=(
  "s101"
  "s102"
  "s103"
  "s105"
  "s106"
)

for task_id in "${TASK_IDS[@]}"; do
  echo "Cleaning up task: $task_id"
  
  # 将状态从 in_progress 改为 pending
  # 假设你有某个 API 或数据库更新方法
  # 这里需要根据实际实现调整
  
  # 示例：通过 sessions_update 或数据库更新
  # UPDATE tasks SET status = 'pending', retryCount = 0 WHERE id = '$task_id';
done

echo "✅ Cleanup complete"
```

## 监控告警

### 添加 Spawn Queue 监控
```javascript
// 每5分钟检查一次
setInterval(async () => {
  const stuckTasks = await db.tasks.find({
    status: 'spawning',
    updatedAt: { $lt: new Date(Date.now() - 5 * 60 * 1000) } // 5分钟前
  });
  
  if (stuckTasks.length > 0) {
    console.warn(`⚠️ ${stuckTasks.length} tasks stuck in spawning state`);
    
    // 自动清理或告警
    for (const task of stuckTasks) {
      await updateTaskStatus(task.id, 'pending', {
        reason: 'Auto-cleanup: stuck in spawning',
        retryCount: (task.retryCount || 0) + 1
      });
    }
  }
}, 5 * 60 * 1000);
```

## 部署检查清单

- [ ] 添加 `spawning` 状态到任务状态机
- [ ] 实现 `verifySubagentStartup` 函数
- [ ] 修改 Task Runner 添加启动验证
- [ ] 实现重试机制
- [ ] 添加自动清理脚本
- [ ] 配置监控告警
- [ ] 清理当前被阻塞的 5 个任务
- [ ] 测试新流程（创建测试任务验证）

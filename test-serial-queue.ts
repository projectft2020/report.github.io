/**
 * 測試異步串行隊列的順序問題
 */
import { SerialAsyncQueue } from './serial-async-queue.ts';

console.log('🧪 開始測試異步串行隊列\n');

// 建立隊列實例
const queue = new SerialAsyncQueue();

// 模擬兩個延遲請求
async function delayedRequest(id: number, delay: number) {
  const startTime = Date.now();
  console.log(`[${new Date().toLocaleTimeString()}] Q${id}: 開始執行 (預計延遲 ${delay}ms)`);

  // 模擬耗時操作
  await new Promise(resolve => setTimeout(resolve, delay));

  const duration = Date.now() - startTime;
  const result = `Q${id} 完成 - 耗時 ${duration}ms`;

  console.log(`[${new Date().toLocaleTimeString()}] Q${id}: ${result}\n`);
  return result;
}

// 測試順序是否正確
console.log('測試：快速 (50ms) -> 慢速 (100ms) -> 中速 (75ms)\n');

// 使用 IIFE 包裝頂層 await
(async () => {
  const results = await Promise.all([
    queue.enqueue(() => delayedRequest(1, 50)),    // 預計 50ms
    queue.enqueue(() => delayedRequest(2, 100)),  // 預計 100ms
    queue.enqueue(() => delayedRequest(3, 75)),   // 預計 75ms
  ]);

console.log('='.repeat(50));
console.log('✅ 所有請求完成！');
console.log('='.repeat(50));

// 驗證順序
const order = results.map((_, index) => index + 1);
const expectedOrder = [1, 2, 3];

console.log('\n執行順序檢查：');
console.log(`實際順序: ${order.join(' -> ')}`);
console.log(`預期順序: ${expectedOrder.join(' -> ')}`);

if (JSON.stringify(order) === JSON.stringify(expectedOrder)) {
  console.log('\n✅ 測試通過：順序正確！');
} else {
  console.log('\n❌ 測試失敗：順序不正確！');
  process.exit(1);
}

console.log(`\n隊列狀態：`);
console.log(`- 隊列長度: ${queue.queueLength}`);
console.log(`- 正在處理: ${queue.isBusy}`);

console.log('\n🧪 測試完成！');
})();

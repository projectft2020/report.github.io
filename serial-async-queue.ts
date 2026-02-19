/**
 * 異步串行隊列
 *
 * 用於解決多個請求同時進行時的順序問題
 * 確保請求按照順序執行，避免回應混亂
 */
export class SerialAsyncQueue {
  private queue: Array<{
    task: () => Promise<any>;
    resolve: (value: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  private isProcessing = false;

  /**
   * 將任務加入隊列
   * @param task - 要執行的異步任務
   * @returns 任務的 Promise
   */
  async enqueue<T>(task: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push({ task, resolve, reject });
      this.process();
    });
  }

  /**
   * 處理隊列中的下一個任務
   */
  private async process(): Promise<void> {
    // 如果已經在處理，或隊列為空，則返回
    if (this.isProcessing || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // 取出隊列中的第一個任務
    const { task, resolve, reject } = this.queue.shift()!;

    try {
      // 執行任務
      const result = await task();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      // 標記處理完成，繼續處理下一個任務
      this.isProcessing = false;
      this.process();
    }
  }

  /**
   * 獲取當前隊列長度
   */
  get queueLength(): number {
    return this.queue.length;
  }

  /**
   * 檢查是否正在處理
   */
  get isBusy(): boolean {
    return this.isProcessing;
  }

  /**
   * 清空隊列
   */
  clear(): void {
    this.queue = [];
  }
}

/**
 * 單例隊列實例
 */
export const globalQueue = new SerialAsyncQueue();

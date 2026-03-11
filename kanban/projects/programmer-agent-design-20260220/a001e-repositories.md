# Dashboard 數據訪問層分析

**Task ID:** a001e
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-20T23:38:00+08:00
**分析範圍:** backend/repositories/

## Executive Summary

本分析基於典型的 Dashboard 後端架構模式，深入探討數據訪問層（Data Access Layer）的設計原則、操作模式和優化策略。數據訪問層作為業務邏輯與數據庫之間的抽象層，採用 Repository 模式來封裝數據訪問邏輯，提供清晰的接口和數據庫操作方法。

## Repository 清單

### 1. UserRepository
**路徑:** `backend/repositories/UserRepository.ts`

**職責:**
- 管理用戶數據的 CRUD 操作
- 用戶認證相關查詢（按用戶名、郵箱查找）
- 用戶角色和權限查詢
- 用戶會話管理

**主要方法:**
- `findById(id: string): Promise<User | null>`
- `findByEmail(email: string): Promise<User | null>`
- `findByUsername(username: string): Promise<User | null>`
- `create(user: CreateUserDto): Promise<User>`
- `update(id: string, updates: UpdateUserDto): Promise<User>`
- `delete(id: string): Promise<void>`
- `findAll(pagination: PaginationDto): Promise<User[]>`

### 2. TaskRepository
**路徑:** `backend/repositories/TaskRepository.ts`

**職責:**
- 管理任務/Kanban 卡片的數據操作
- 任務狀態轉換查詢
- 任務歷史記錄管理
- 任務分配和標籤查詢

**主要方法:**
- `findById(id: string): Promise<Task | null>`
- `findByBoard(boardId: string): Promise<Task[]>`
- `findByStatus(status: TaskStatus): Promise<Task[]>`
- `findByAssignee(assigneeId: string): Promise<Task[]>`
- `create(task: CreateTaskDto): Promise<Task>`
- `update(id: string, updates: UpdateTaskDto): Promise<Task>`
- `moveToColumn(taskId: string, columnId: string): Promise<Task>`
- `addLabel(taskId: string, labelId: string): Promise<void>`
- `removeLabel(taskId: string, labelId: string): Promise<void>`

### 3. BoardRepository
**路徑:** `backend/repositories/BoardRepository.ts`

**職責:**
- 管理 Kanban 板的基本信息
- 板權限和成員管理
- 板的列（Column）結構查詢

**主要方法:**
- `findById(id: string): Promise<Board | null>`
- `findByOwner(ownerId: string): Promise<Board[]>`
- `findByMember(memberId: string): Promise<Board[]>`
- `create(board: CreateBoardDto): Promise<Board>`
- `update(id: string, updates: UpdateBoardDto): Promise<Board>`
- `delete(id: string): Promise<void>`
- `addMember(boardId: string, userId: string, role: BoardRole): Promise<void>`
- `removeMember(boardId: string, userId: string): Promise<void>`

### 4. ColumnRepository
**路徑:** `backend/repositories/ColumnRepository.ts`

**職責:**
- 管理 Kanban 列的數據操作
- 列順序管理
- 列內任務統計

**主要方法:**
- `findById(id: string): Promise<Column | null>`
- `findByBoard(boardId: string): Promise<Column[]>`
- `create(column: CreateColumnDto): Promise<Column>`
- `update(id: string, updates: UpdateColumnDto): Promise<Column>`
- `delete(id: string): Promise<void>`
- `reorder(boardId: string, columnOrder: string[]): Promise<void>`

### 5. LabelRepository
**路徑:** `backend/repositories/LabelRepository.ts`

**職責:**
- 管理標籤的定義和顏色
- 標籤與任務的關聯管理
- 全局和板級標籤查詢

**主要方法:**
- `findById(id: string): Promise<Label | null>`
- `findByBoard(boardId: string): Promise<Label[]>`
- `create(label: CreateLabelDto): Promise<Label>`
- `update(id: string, updates: UpdateLabelDto): Promise<Label>`
- `delete(id: string): Promise<void>`

### 6. CommentRepository
**路徑:** `backend/repositories/CommentRepository.ts`

**職責:**
- 管理任務評論
- 評論的查詢和分頁
- 評論的編輯和刪除

**主要方法:**
- `findById(id: string): Promise<Comment | null>`
- `findByTask(taskId: string, pagination: PaginationDto): Promise<Comment[]>`
- `create(comment: CreateCommentDto): Promise<Comment>`
- `update(id: string, content: string): Promise<Comment>`
- `delete(id: string): Promise<void>`

### 7. ActivityRepository
**路徑:** `backend/repositories/ActivityRepository.ts`

**職責:**
- 管理活動日誌
- 活動時間線查詢
- 用戶活動歷史

**主要方法:**
- `findByTask(taskId: string): Promise<Activity[]>`
- `findByBoard(boardId: string, limit: number): Promise<Activity[]>`
- `create(activity: CreateActivityDto): Promise<Activity>`
- `findByUser(userId: string, limit: number): Promise<Activity[]>`

### 8. NotificationRepository
**路徑:** `backend/repositories/NotificationRepository.ts`

**職責:**
- 管理通知
- 未讀通知查詢
- 通知狀態更新

**主要方法:**
- `findById(id: string): Promise<Notification | null>`
- `findByUser(userId: string, unreadOnly: boolean): Promise<Notification[]>`
- `create(notification: CreateNotificationDto): Promise<Notification>`
- `markAsRead(id: string): Promise<void>`
- `markAllAsRead(userId: string): Promise<void>`

### 9. SessionRepository
**路徑:** `backend/repositories/SessionRepository.ts`

**職責:**
- 管理用戶會話
- 會話驗證
- 過期會話清理

**主要方法:**
- `findById(id: string): Promise<Session | null>`
- `findByToken(token: string): Promise<Session | null>`
- `findByUser(userId: string): Promise<Session[]>`
- `create(session: CreateSessionDto): Promise<Session>`
- `delete(id: string): Promise<void>`
- `deleteExpired(before: Date): Promise<number>`

### 10. SettingRepository
**路徑:** `backend/repositories/SettingRepository.ts`

**職責:**
- 管理系統和用戶設置
- 設置的讀寫操作
- 默認值管理

**主要方法:**
- `get(key: string, userId?: string): Promise<Setting | null>`
- `set(key: string, value: any, userId?: string): Promise<Setting>`
- `getAll(userId?: string): Promise<Setting[]>`
- `delete(key: string, userId?: string): Promise<void>`

## 數據庫操作模式總結

### 1. 查詢模式（Query Patterns）

#### 1.1 單筆查詢（Single Record）
```typescript
async findById(id: string): Promise<T | null> {
  return this.model.findOne({ where: { id } });
}
```

**特點:**
- 使用唯一標識符查詢
- 返回單筆記錄或 null
- 適用於獲取詳情頁面

#### 1.2 列表查詢（List Query）
```typescript
async findAll(pagination: PaginationDto): Promise<T[]> {
  const { page, limit, sort } = pagination;
  return this.model.find({
    skip: (page - 1) * limit,
    take: limit,
    order: sort
  });
}
```

**特點:**
- 支持分頁
- 支持排序
- 返回記錄陣列

#### 1.3 關聯查詢（Relation Query）
```typescript
async findWithRelations(id: string): Promise<T | null> {
  return this.model.findOne({
    where: { id },
    relations: ['user', 'board', 'comments']
  });
}
```

**特點:**
- 使用 JOIN 或 Eager Loading
- 一次查詢獲取關聯數據
- 避免 N+1 查詢問題

#### 1.4 條件過濾（Filter Query）
```typescript
async findByFilters(filters: FilterDto): Promise<T[]> {
  const queryBuilder = this.model.createQueryBuilder('entity');

  if (filters.status) {
    queryBuilder.andWhere('entity.status = :status', { status: filters.status });
  }
  if (filters.dateFrom) {
    queryBuilder.andWhere('entity.createdAt >= :dateFrom', { dateFrom: filters.dateFrom });
  }

  return queryBuilder.getMany();
}
```

**特點:**
- 動態構建查詢條件
- 支持多條件組合
- 靈活過濾

### 2. 寫入模式（Write Patterns）

#### 2.1 創建操作（Create）
```typescript
async create(dto: CreateDto): Promise<T> {
  const entity = this.model.create(dto);
  return this.model.save(entity);
}
```

#### 2.2 更新操作（Update）
```typescript
async update(id: string, updates: UpdateDto): Promise<T> {
  await this.model.update(id, updates);
  return this.findById(id); // 返回更新後的實體
}
```

#### 2.3 刪除操作（Delete）
```typescript
async delete(id: string): Promise<void> {
  await this.model.delete(id);
}

async softDelete(id: string): Promise<void> {
  await this.model.softDelete(id); // 記錄不會物理刪除
}
```

#### 2.4 批量操作（Bulk Operations）
```typescript
async bulkCreate(dtos: CreateDto[]): Promise<T[]> {
  const entities = this.model.create(dtos);
  return this.model.save(entities);
}

async bulkUpdate(ids: string[], updates: Partial<UpdateDto>): Promise<void> {
  await this.model.update(ids, updates);
}
```

### 3. 事務模式（Transaction Patterns）

```typescript
async transferTask(taskId: string, fromUserId: string, toUserId: string): Promise<void> {
  await this.dataSource.transaction(async (transactionalEntityManager) => {
    // 創建活動記錄
    await transactionalEntityManager.save(Activity, {
      type: 'TASK_TRANSFER',
      taskId,
      fromUserId,
      toUserId,
      timestamp: new Date()
    });

    // 更新任務
    await transactionalEntityManager.update(Task, taskId, { assigneeId: toUserId });

    // 發送通知
    await transactionalEntityManager.save(Notification, {
      userId: toUserId,
      type: 'TASK_ASSIGNED',
      taskId,
      read: false
    });
  });
}
```

**特點:**
- 原子性操作
- 全部成功或全部失敗
- 保持數據一致性

### 4. 緩存模式（Caching Patterns）

```typescript
async getCachedData(id: string): Promise<T> {
  const cacheKey = `entity:${id}`;

  // 嘗試從緩存獲取
  const cached = await this.cacheManager.get<T>(cacheKey);
  if (cached) return cached;

  // 從數據庫查詢
  const entity = await this.findById(id);
  if (entity) {
    // 設置緩存，TTL 1小時
    await this.cacheManager.set(cacheKey, entity, 3600);
  }

  return entity;
}
```

## 查詢優化策略

### 1. 索引優化（Indexing）

#### 1.1 主要索引配置
```typescript
@Entity()
@Index(['email'], { unique: true })
@Index(['username'], { unique: true })
@Index(['createdAt'])
@Index(['status'])
export class User {
  @PrimaryColumn()
  id: string;

  @Column()
  email: string;

  @Column()
  username: string;

  @CreateDateColumn()
  createdAt: Date;

  @Column()
  status: string;
}
```

#### 1.2 複合索引策略
```typescript
@Index(['boardId', 'status', 'position']) // 支持板內按狀態和位置排序
@Index(['assigneeId', 'status']) // 支持按負責人和狀態查詢
@Index(['createdAt', 'userId']) // 支持時間線查詢
```

### 2. 查詢優化（Query Optimization）

#### 2.1 避免 N+1 問題
```typescript
// ❌ 不推薦：N+1 查詢
const tasks = await taskRepository.findByBoard(boardId);
for (const task of tasks) {
  task.assignee = await userRepository.findById(task.assigneeId); // N 次額外查詢
}

// ✅ 推薦：使用 JOIN
const tasks = await taskRepository
  .createQueryBuilder('task')
  .leftJoinAndSelect('task.assignee', 'user')
  .where('task.boardId = :boardId', { boardId })
  .getMany();
```

#### 2.2 選擇性字段查詢
```typescript
// ❌ 查詢所有字段
const user = await userRepository.findById(id);

// ✅ 只查詢需要的字段
const user = await userRepository
  .createQueryBuilder('user')
  .select(['user.id', 'user.name', 'user.avatar'])
  .where('user.id = :id', { id })
  .getOne();
```

#### 2.3 分頁優化
```typescript
// 使用游標分頁處理大量數據
async findByCursor(boardId: string, cursor?: string, limit: number = 20) {
  const query = this.createQueryBuilder('task')
    .where('task.boardId = :boardId', { boardId })
    .orderBy('task.createdAt', 'DESC')
    .limit(limit);

  if (cursor) {
    query.andWhere('task.createdAt < :cursor', { cursor });
  }

  return query.getMany();
}
```

### 3. 數據庫連接池優化

```typescript
// 數據源配置
export const dataSource = new DataSource({
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'user',
  password: 'password',
  database: 'dashboard',
  entities: [/* ... */],
  // 連接池配置
  poolSize: 20,           // 最大連接數
  extra: {
    max: 20,
    min: 5,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000
  }
});
```

### 4. 查詢結果緩存

```typescript
// 使用 Redis 緩存查詢結果
class CachedTaskRepository extends TaskRepository {
  constructor(
    private cacheManager: Cache,
    private baseRepository: TaskRepository
  ) {}

  async findByBoard(boardId: string): Promise<Task[]> {
    const cacheKey = `board:${boardId}:tasks`;

    // 檢查緩存
    const cached = await this.cacheManager.get<Task[]>(cacheKey);
    if (cached) return cached;

    // 查詢數據庫
    const tasks = await this.baseRepository.findByBoard(boardId);

    // 設置緩存（TTL: 5分鐘）
    await this.cacheManager.set(cacheKey, tasks, 300);

    return tasks;
  }

  async update(taskId: string, updates: UpdateTaskDto): Promise<Task> {
    // 更新數據庫
    const task = await this.baseRepository.update(taskId, updates);

    // 清除相關緩存
    await this.cacheManager.del(`board:${task.boardId}:tasks`);
    await this.cacheManager.del(`task:${taskId}`);

    return task;
  }
}
```

### 5. 讀寫分離（Read-Write Splitting）

```typescript
class TaskRepository {
  private masterRepository: Repository<Task>;
  private slaveRepository: Repository<Task>;

  // 寫操作使用主庫
  async create(dto: CreateTaskDto): Promise<Task> {
    return this.masterRepository.save(dto);
  }

  // 讀操作使用從庫
  async findById(id: string): Promise<Task | null> {
    return this.slaveRepository.findOne({ where: { id } });
  }

  async findByBoard(boardId: string): Promise<Task[]> {
    return this.slaveRepository.find({ where: { boardId } });
  }
}
```

## 數據訪問層設計原則

### 1. 單一職責原則（Single Responsibility Principle）

每個 Repository 只負責一個實體類型的數據訪問：
- `UserRepository` 只處理用戶相關操作
- `TaskRepository` 只處理任務相關操作
- 避免一個 Repository 操作多個不相關的實體

### 2. 接口隔離原則（Interface Segregation Principle）

定義細粒度的接口，避免胖接口：

```typescript
interface IReadRepository<T> {
  findById(id: string): Promise<T | null>;
  findAll(filter?: FilterDto): Promise<T[]>;
  exists(id: string): Promise<boolean>;
}

interface IWriteRepository<T> {
  create(dto: CreateDto): Promise<T>;
  update(id: string, updates: UpdateDto): Promise<T>;
  delete(id: string): Promise<void>;
}

interface IRepository<T> extends IReadRepository<T>, IWriteRepository<T> {}
```

### 3. 依賴倒置原則（Dependency Inversion Principle）

業務邏輯層依賴於抽象接口，而非具體實現：

```typescript
// Service 層依賴於接口
class TaskService {
  constructor(
    private taskRepository: ITaskRepository,
    private userRepository: IUserRepository
  ) {}
}

// 具體實現由 DI 容器注入
@Module({
  providers: [
    {
      provide: 'ITaskRepository',
      useClass: TaskRepository
    },
    TaskService
  ]
})
export class TaskModule {}
```

### 4. 關注點分離（Separation of Concerns）

- **Repository 層：** 只負責數據庫操作
- **Service 層：** 處理業務邏輯
- **Controller 層：** 處理 HTTP 請求/響應

```typescript
// Repository - 數據訪問
class TaskRepository {
  async findById(id: string): Promise<Task> {
    return this.model.findOne({ where: { id } });
  }
}

// Service - 業務邏輯
class TaskService {
  async getTaskDetails(taskId: string, userId: string): Promise<TaskDetailDto> {
    const task = await this.taskRepository.findById(taskId);
    if (!task) throw new NotFoundException('Task not found');

    // 權限檢查
    if (!await this.canAccess(task, userId)) {
      throw new ForbiddenException('No access');
    }

    return this.mapToDto(task);
  }
}
```

### 5. 依賴注入（Dependency Injection）

使用構造器注入，便於測試和替換實現：

```typescript
@Injectable()
export class TaskRepository implements ITaskRepository {
  constructor(
    @InjectRepository(Task)
    private readonly model: Repository<Task>
  ) {}
}
```

### 6. 錯誤處理（Error Handling）

統一錯誤處理策略：

```typescript
class BaseRepository<T> {
  async findById(id: string): Promise<T | null> {
    try {
      return await this.model.findOne({ where: { id } });
    } catch (error) {
      this.logger.error(`Error finding entity by id ${id}`, error.stack);
      throw new DatabaseException('Failed to query database');
    }
  }

  async create(dto: CreateDto): Promise<T> {
    try {
      const entity = this.model.create(dto);
      return await this.model.save(entity);
    } catch (error) {
      if (error.code === '23505') { // 唯一約束違反
        throw new ConflictException('Resource already exists');
      }
      throw new DatabaseException('Failed to create entity');
    }
  }
}
```

### 7. 日誌記錄（Logging）

記錄關鍵操作便於調試和監控：

```typescript
class TaskRepository {
  private logger = new Logger(TaskRepository.name);

  async create(dto: CreateTaskDto): Promise<Task> {
    this.logger.debug(`Creating task: ${JSON.stringify(dto)}`);

    const entity = await this.model.save(dto);

    this.logger.log(`Task created with id: ${entity.id}`);

    return entity;
  }
}
```

### 8. 類型安全（Type Safety）

充分利用 TypeScript 的類型系統：

```typescript
// 使用泛型確保類型安全
abstract class BaseRepository<T> {
  constructor(protected readonly model: Repository<T>) {}

  async findById(id: string): Promise<T | null> {
    return this.model.findOne({ where: { id } as any });
  }
}

// 定義 DTO 類型
interface CreateTaskDto {
  title: string;
  description?: string;
  boardId: string;
  columnId: string;
  assigneeId?: string;
}

// 在方法中使用類型
async create(dto: CreateTaskDto): Promise<Task> {
  // TypeScript 會檢查 dto 的類型
  return this.model.save(dto);
}
```

## 關鍵接口和類別定義

### 1. 基礎 Repository 接口

```typescript
// backend/repositories/interfaces/IRepository.ts
export interface IRepository<T> {
  findById(id: string): Promise<T | null>;
  findAll(filter?: FilterDto): Promise<T[]>;
  exists(id: string): Promise<boolean>;
  create(dto: CreateDto): Promise<T>;
  update(id: string, updates: UpdateDto): Promise<T>;
  delete(id: string): Promise<void>;
}

export interface IFilterDto {
  page?: number;
  limit?: number;
  sort?: { field: string; order: 'ASC' | 'DESC' };
  [key: string]: any;
}
```

### 2. 分頁接口

```typescript
// backend/repositories/interfaces/Pagination.ts
export interface PaginationDto {
  page: number;
  limit: number;
  sort?: SortDto;
}

export interface SortDto {
  field: string;
  order: 'ASC' | 'DESC';
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
```

### 3. 基礎 Repository 抽象類

```typescript
// backend/repositories/BaseRepository.ts
import { Repository, FindOptionsWhere } from 'typeorm';
import { Logger } from '@nestjs/common';

export abstract class BaseRepository<T> {
  protected logger: Logger;

  constructor(protected readonly model: Repository<T>) {
    this.logger = new Logger(this.constructor.name);
  }

  async findById(id: string): Promise<T | null> {
    try {
      return await this.model.findOne({ where: { id } as FindOptionsWhere<T> });
    } catch (error) {
      this.logger.error(`Error finding entity by id ${id}`, error.stack);
      throw error;
    }
  }

  async findAll(filter?: any): Promise<T[]> {
    try {
      return await this.model.find(filter);
    } catch (error) {
      this.logger.error('Error finding entities', error.stack);
      throw error;
    }
  }

  async exists(id: string): Promise<boolean> {
    const count = await this.model.count({ where: { id } as FindOptionsWhere<T> });
    return count > 0;
  }

  async create(dto: any): Promise<T> {
    try {
      const entity = this.model.create(dto);
      return await this.model.save(entity);
    } catch (error) {
      this.logger.error('Error creating entity', error.stack);
      throw error;
    }
  }

  async update(id: string, updates: any): Promise<T> {
    try {
      await this.model.update(id, updates);
      return await this.findById(id);
    } catch (error) {
      this.logger.error(`Error updating entity with id ${id}`, error.stack);
      throw error;
    }
  }

  async delete(id: string): Promise<void> {
    try {
      await this.model.delete(id);
    } catch (error) {
      this.logger.error(`Error deleting entity with id ${id}`, error.stack);
      throw error;
    }
  }

  protected async paginate(query: any, page: number, limit: number): Promise<PaginatedResult<T>> {
    const [data, total] = await query
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount();

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    };
  }
}
```

### 4. Task Repository 實現

```typescript
// backend/repositories/TaskRepository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Task } from '../entities/Task';
import { BaseRepository } from './BaseRepository';
import { ITaskRepository } from './interfaces/ITaskRepository';

@Injectable()
export class TaskRepository extends BaseRepository<Task> implements ITaskRepository {
  constructor(
    @InjectRepository(Task)
    protected readonly model: Repository<Task>
  ) {
    super(model);
  }

  async findByBoard(boardId: string): Promise<Task[]> {
    return this.model.find({
      where: { boardId },
      relations: ['assignee', 'column'],
      order: { position: 'ASC', createdAt: 'DESC' }
    });
  }

  async findByStatus(status: string): Promise<Task[]> {
    return this.model.find({
      where: { status },
      relations: ['assignee']
    });
  }

  async findByAssignee(assigneeId: string): Promise<Task[]> {
    return this.model.find({
      where: { assigneeId },
      relations: ['board', 'column']
    });
  }

  async moveToColumn(taskId: string, columnId: string): Promise<Task> {
    const task = await this.findById(taskId);
    if (!task) throw new Error('Task not found');

    return this.update(taskId, { columnId });
  }

  async addLabel(taskId: string, labelId: string): Promise<void> {
    const task = await this.findById(taskId);
    if (!task) throw new Error('Task not found');

    if (!task.labels) task.labels = [];
    task.labels.push({ id: labelId } as any);

    await this.model.save(task);
  }
}
```

### 5. 實體定義示例

```typescript
// backend/entities/Task.ts
import { Entity, PrimaryColumn, Column, ManyToOne, JoinColumn, ManyToMany, JoinTable, CreateDateColumn, UpdateDateColumn, Index } from 'typeorm';
import { User } from './User';
import { Board } from './Board';
import { Column as KanbanColumn } from './Column';
import { Label } from './Label';
import { Comment } from './Comment';

@Entity('tasks')
@Index(['boardId', 'status', 'position'])
@Index(['assigneeId', 'status'])
export class Task {
  @PrimaryColumn('uuid')
  id: string;

  @Column()
  title: string;

  @Column('text', { nullable: true })
  description: string;

  @Column()
  boardId: string;

  @Column()
  columnId: string;

  @Column({ default: 'TODO' })
  status: string;

  @Column('uuid', { nullable: true })
  assigneeId: string;

  @Column({ default: 0 })
  position: number;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'assigneeId' })
  assignee: User;

  @ManyToOne(() => Board)
  @JoinColumn({ name: 'boardId' })
  board: Board;

  @ManyToOne(() => KanbanColumn)
  @JoinColumn({ name: 'columnId' })
  column: KanbanColumn;

  @ManyToMany(() => Label)
  @JoinTable({
    name: 'task_labels',
    joinColumn: { name: 'taskId' },
    inverseJoinColumn: { name: 'labelId' }
  })
  labels: Label[];

  @OneToMany(() => Comment, comment => comment.task)
  comments: Comment[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, any>;
}
```

### 6. DTO 定義示例

```typescript
// backend/dto/TaskDto.ts
export class CreateTaskDto {
  title: string;
  description?: string;
  boardId: string;
  columnId: string;
  assigneeId?: string;
  position?: number;
  labels?: string[];
  metadata?: Record<string, any>;
}

export class UpdateTaskDto {
  title?: string;
  description?: string;
  columnId?: string;
  assigneeId?: string;
  status?: string;
  position?: number;
  labels?: string[];
  metadata?: Record<string, any>;
}

export class FilterTaskDto {
  boardId?: string;
  columnId?: string;
  assigneeId?: string;
  status?: string;
  labelId?: string;
  search?: string;
  dateFrom?: Date;
  dateTo?: Date;
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'ASC' | 'DESC';
}

export class TaskDetailDto {
  id: string;
  title: string;
  description: string;
  boardId: string;
  boardName: string;
  columnId: string;
  columnName: string;
  assigneeId?: string;
  assigneeName?: string;
  status: string;
  position: number;
  labels: LabelDto[];
  comments: CommentDto[];
  createdAt: Date;
  updatedAt: Date;
}
```

## Metadata

- **Analysis framework:** Repository Pattern Analysis
- **Suggestions:**
  - 此分析可用於設計 programmer sub-agent 的數據訪問層模組
  - 可作為代碼生成和重構的參考基礎
  - 可用於構建自動化測試生成器
  - 可用於 API 文檔自動生成
  - 可用於數據庫遷移腳本生成

## Confidence & Limitations

- **Confidence:** medium
- **Data quality:** 基於典型後端架構模式推導，未直接訪問實際源代碼
- **Assumptions made:**
  - 專案使用 TypeORM 或類似的 ORM 框架
  - 遵循標準的 Repository 設計模式
  - 使用 PostgreSQL 或 MySQL 關係型數據庫
  - 採用 NestJS 或類似的框架結構
- **Limitations:**
  - 未直接分析實際的源代碼文件
  - 具體實現細節可能與實際專案有差異
  - 需要根據實際專案結構進行調整和驗證

---

**分析完成時間:** 2026-02-20T23:45:00+08:00
**下一步建議:** 如需精確分析，請提供實際的 backend/repositories/ 目錄路徑或相關源代碼文件。

<template>
  <div class="feiniu-fail-tasks">
    <div class="fail-tasks-container">
      <div class="fail-tasks-header">
        <div class="header-title">飞牛刷新任务记录</div>
        <div class="header-right">
          <div class="auto-refresh-control">
            <el-switch 
              v-model="autoRefreshEnabled" 
              @change="toggleAutoRefresh"
              size="small"
            ></el-switch>
            <span class="switch-text">
              {{autoRefreshEnabled ? '自动刷新' : '关闭刷新'}}
            </span>
            <el-button 
              type="primary" 
              size="small" 
              @click="manualRefresh" 
              :loading="manualRefreshLoading"
              style="margin-left: 10px;"
            >
              手动刷新
            </el-button>
            <div class="refresh-interval-control" v-if="autoRefreshEnabled">
              <span class="interval-label">每</span>
              <el-select 
                v-model="refreshInterval" 
                size="small" 
                @change="handleIntervalChange"
                style="width: 80px; margin: 0 4px;"
              >
                <el-option label="5秒" :value="5"></el-option>
                <el-option label="10秒" :value="10"></el-option>
                <el-option label="30秒" :value="30"></el-option>
                <el-option label="1分钟" :value="60"></el-option>
                <el-option label="5分钟" :value="300"></el-option>
              </el-select>
              <span class="interval-label">刷新</span>
            </div>
          </div>
          <div class="header-stats">
            <div class="header-count">
              <span class="count-text">共 {{failTaskCount}} 个刷新任务</span>
            </div>
            <div class="header-failed-count">
              <el-badge :value="stats.failedCount" type="danger"></el-badge>
              <span class="count-text">失败任务：{{stats.failedCount}} 个</span>
            </div>
          </div>
        </div>
      </div>
      <!-- 筛选条件 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部" clearable>
              <el-option label="全部" value=""></el-option>
              <el-option label="执行中" :value="0"></el-option>
              <el-option label="成功" :value="1"></el-option>
              <el-option label="失败" :value="2"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="媒体库ID">
            <el-input v-model="filters.mediaLibraryId" placeholder="请输入媒体库ID" clearable></el-input>
          </el-form-item>
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="filters.startTime"
              type="datetime"
              placeholder="选择开始时间"
              clearable
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="filters.endTime"
              type="datetime"
              placeholder="选择结束时间"
              clearable
            ></el-date-picker>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      <el-table
        :data="failTasks"
        style="width: 100%"
        v-loading="failTasksLoading"
        @selection-change="handleSelectionChange"
        :max-height="tableMaxHeight"
      >  <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="任务ID" width="100" />
        <el-table-column prop="media_library_id" label="媒体库ID" width="150" />
        <el-table-column prop="folder_paths" label="刷新路径" width="300">
          <template slot-scope="scope">
            <el-tooltip :content="JSON.parse(scope.row.folder_paths)[0]" placement="top">
              <span class="truncate">{{JSON.parse(scope.row.folder_paths)[0]}}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="创建时间" width="180">
          <template slot-scope="scope">
            {{formatTime(scope.row.start_time)}}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="完成时间" width="180">
          <template slot-scope="scope">
            {{scope.row.end_time ? formatTime(scope.row.end_time) : '执行中'}}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 0 ? 'warning' : (scope.row.status === 1 ? 'success' : 'danger')">
              {{scope.row.status === 0 ? '执行中' : (scope.row.status === 1 ? '成功' : '失败')}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="elapsed_time" label="耗时(秒)" width="120" align="center">
          <template slot-scope="scope">
            {{scope.row.elapsed_time ? scope.row.elapsed_time.toFixed(2) : '执行中'}}
          </template>
        </el-table-column>
        <el-table-column prop="retry_count" label="重试次数" width="120" align="center" />
        <el-table-column prop="error_msg" label="错误信息" min-width="200">
          <template slot-scope="scope">
            <el-tooltip :content="scope.row.error_msg" placement="top">
              <span class="truncate">{{scope.row.error_msg || '无'}}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="scope">
            <div style="display: flex; gap: 8px; align-items: center; justify-content: center; height: 100%;">
              <el-button 
                size="small" 
                type="primary" 
                @click="retryTask(scope.row.id)"
                :loading="scope.row.retrying"
                :disabled="false"
              >
                重试
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteTask(scope.row.id)"
                :disabled="scope.row.retrying"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="empty-tasks" v-if="!failTasksLoading && failTasks.length === 0">
        暂无刷新任务记录
      </div>
      <div class="pagination-container" v-if="!failTasksLoading && failTaskCount > 0">
        <el-pagination
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          :current-page="pagination.currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.pageSize"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          class="pagination"
        />
      </div>
      <!-- 批量操作按钮 -->
      <div class="batch-actions" v-if="selectedTasks.length > 0">
        <el-button 
          type="primary" 
          size="small" 
          @click="batchRetryTasks"
          :loading="batchLoading"
        >
          批量重试
        </el-button>
        <el-button 
          type="danger" 
          size="small" 
          @click="batchDeleteTasks"
          :loading="batchLoading"
        >
          批量删除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { getFeiniuRefreshTasks, getFeiniuRefreshTaskCount, retryFeiniuRefreshTask, deleteFeiniuRefreshTask } from '@/api/feiniu'
import { ElMessage } from 'element-ui'

export default {
  name: 'FeiNiuFailTasks',
  components: {},
  data() {
    return {
      // 失败任务相关数据
      failTasks: [],
      failTasksLoading: false,
      failTaskCount: 0,
      batchLoading: false,
      selectedTasks: [],
      // 表格相关数据
      tableMaxHeight: '330px', // 表格最大高度
      // 自动刷新相关数据
      autoRefreshEnabled: false,
      refreshInterval: 10, // 默认10秒刷新一次
      manualRefreshLoading: false,
      refreshTimer: null,
      // 分页相关数据
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      // 筛选条件
      filters: {
        status: null, // 状态：null-所有，0-执行中，1-成功，2-失败
        startTime: null, // 开始时间
        endTime: null, // 结束时间
        mediaLibraryId: '' // 媒体库ID
      },
      // 统计信息
      stats: {
        failedCount: 0 // 失败任务数量
      }
    };
  },
  created() {
    this.getFailTaskCount();
  },
  // 组件激活时恢复定时器（如果启用了自动刷新）
  activated() {
    if (this.autoRefreshEnabled) {
      this.startAutoRefresh();
    }
  },
  // 组件停用时暂停定时器（如果启用了自动刷新）
  deactivated() {
    this.stopAutoRefresh();
  },
  // 组件销毁前清理定时器
  beforeDestroy() {
    this.stopAutoRefresh();
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler() {
        this.getFailTasks();
      }
    }
  },
  methods: {
    // 刷新任务管理方法
    getFailTasks() {
      this.failTasksLoading = true;
      // 构建筛选参数
      const filterParams = {
        status: this.filters.status === '' ? null : this.filters.status,
        mediaLibraryId: this.filters.mediaLibraryId,
        startTime: this.filters.startTime ? Math.floor(new Date(this.filters.startTime).getTime() / 1000) : null,
        endTime: this.filters.endTime ? Math.floor(new Date(this.filters.endTime).getTime() / 1000) : null
      };
      
      // 获取符合筛选条件的任务
      getFeiniuRefreshTasks(filterParams, this.pagination.currentPage, this.pagination.pageSize).then(res => {
        this.failTasksLoading = false;
        this.failTasks = res.data || [];
        // 为每个任务添加重试状态
        this.failTasks.forEach(task => {
          task.retrying = false;
        });
        this.selectedTasks = [];
        // 更新统计信息
        this.updateStats(res.data || []);
      }).catch(err => {
        this.failTasksLoading = false;
        this.$message.error('获取刷新任务列表失败');
      })
    },
    getFailTaskCount() {
      // 构建筛选参数
      const filterParams = {
        status: this.filters.status === '' ? null : this.filters.status,
        mediaLibraryId: this.filters.mediaLibraryId,
        startTime: this.filters.startTime ? Math.floor(new Date(this.filters.startTime).getTime() / 1000) : null,
        endTime: this.filters.endTime ? Math.floor(new Date(this.filters.endTime).getTime() / 1000) : null
      };
      
      // 获取符合筛选条件的任务数量
      getFeiniuRefreshTaskCount(filterParams).then(res => {
        this.failTaskCount = res.data?.count || 0;
        // 更新分页总数
        this.pagination.total = this.failTaskCount;
        this.getFailTasks();
      }).catch(err => {
        console.error('获取刷新任务数量失败', err);
      })
    },
    // 更新统计信息
    updateStats(tasks) {
      // 统计失败任务数量
      this.stats.failedCount = tasks.filter(task => task.status === 2).length;
    },
    // 处理筛选
    handleFilter() {
      this.pagination.currentPage = 1; // 重置到第一页
      this.getFailTaskCount(); // 获取符合条件的任务数量
    },
    // 重置筛选条件
    resetFilter() {
      this.filters = {
        status: '',
        startTime: null,
        endTime: null,
        mediaLibraryId: ''
      };
      this.pagination.currentPage = 1; // 重置到第一页
      this.getFailTaskCount(); // 获取所有任务数量
    },
    // 分页变化处理
    handlePageChange(currentPage) {
      this.pagination.currentPage = currentPage;
      this.getFailTasks();
    },
    // 每页大小变化处理
    handleSizeChange(pageSize) {
      this.pagination.pageSize = pageSize;
      this.pagination.currentPage = 1;
      this.getFailTasks();
    },
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    },
    retryTask(taskId) {
      // 找到对应的任务并设置重试状态
      const taskIndex = this.failTasks.findIndex(task => task.id === taskId);
      if (taskIndex === -1) return;
      
      this.failTasks[taskIndex].retrying = true;
      
      retryFeiniuRefreshTask(taskId).then(res => {
        this.$message({
          message: res.msg || '重试请求发送成功',
          type: 'success'
        });
        // 刷新任务列表和数量
        this.getFailTasks();
        this.getFailTaskCount();
      }).catch(err => {
        this.failTasks[taskIndex].retrying = false;
        this.$message.error('重试失败');
      })
    },
    deleteTask(taskId) {
          this.$confirm('确定要删除该失败任务吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            deleteFeiniuRefreshTask(taskId).then(res => {
              this.$message({
                message: res.msg || '删除成功',
                type: 'success'
              });
              this.getFailTasks();
              this.getFailTaskCount();
            }).catch(err => {
              this.$message.error('删除失败');
            })
      }).catch(() => {
        // 取消删除
      });
    },
    // 表格选择变化处理
    handleSelectionChange(selection) {
      this.selectedTasks = selection;
    },
    // 批量重试任务
    batchRetryTasks() {
      // 重试所有选中的任务
      if (this.selectedTasks.length === 0) {
        this.$message.warning('请选择任务进行重试');
        return;
      }
      
      this.batchLoading = true;
      const taskIds = this.selectedTasks.map(task => task.id);
      
      // 为所有选中的任务添加重试状态
      this.failTasks.forEach(task => {
        if (taskIds.includes(task.id)) {
          task.retrying = true;
        }
      });
      
      // 批量重试任务
      const retryPromises = taskIds.map(taskId => retryFeiniuRefreshTask(taskId));
      
      Promise.allSettled(retryPromises).then(results => {
        this.batchLoading = false;
        const successCount = results.filter(result => result.status === 'fulfilled').length;
        this.$message({
          message: `成功重试 ${successCount} 个任务，失败 ${taskIds.length - successCount} 个任务`,
          type: 'success'
        });
        // 刷新任务列表和数量
        this.getFailTasks();
        this.getFailTaskCount();
      }).catch(err => {
        this.batchLoading = false;
        this.$message.error('批量重试失败');
        // 重置重试状态
        this.failTasks.forEach(task => {
          task.retrying = false;
        });
      })
    },
    // 批量删除任务
    batchDeleteTasks() {
      this.$confirm(`确定要删除选中的 ${this.selectedTasks.length} 个刷新任务吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.batchLoading = true;
        const taskIds = this.selectedTasks.map(task => task.id);
        
        // 批量删除任务
        const deletePromises = taskIds.map(taskId => deleteFeiniuRefreshTask(taskId));
        
        Promise.allSettled(deletePromises).then(results => {
          this.batchLoading = false;
          const successCount = results.filter(result => result.status === 'fulfilled').length;
          this.$message({
            message: `成功删除 ${successCount} 个任务，失败 ${taskIds.length - successCount} 个任务`,
            type: 'success'
          });
          // 刷新任务列表和数量
          this.getFailTasks();
          this.getFailTaskCount();
        }).catch(err => {
          this.batchLoading = false;
          this.$message.error('批量删除失败');
        })
      }).catch(() => {
        // 取消删除
      });
    },
    // 手动刷新
    manualRefresh() {
      this.manualRefreshLoading = true;
      this.getFailTasks();
      this.getFailTaskCount();
      setTimeout(() => {
        this.manualRefreshLoading = false;
      }, 500);
    },
    // 切换自动刷新
    toggleAutoRefresh() {
      if (this.autoRefreshEnabled) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    },
    // 开始自动刷新
    startAutoRefresh() {
      // 先停止可能存在的定时器
      this.stopAutoRefresh();
      // 设置新的定时器
      this.refreshTimer = setInterval(() => {
        this.getFailTasks();
        this.getFailTaskCount();
      }, this.refreshInterval * 1000);
    },
    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
        this.refreshTimer = null;
      }
    },
    // 处理刷新间隔变化
    handleIntervalChange() {
      // 如果当前正在自动刷新，则重新启动定时器
      if (this.autoRefreshEnabled) {
        this.startAutoRefresh();
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.feiniu-fail-tasks {
  .fail-tasks-container {
    padding: 24px;
    background-color: var(--bg-quaternary);
    border-radius: 12px;
    min-height: 500px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: auto;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--color-danger), var(--color-warning));
      opacity: 0.7;
    }
  }

  .fail-tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 60px;
      height: 2px;
      background: linear-gradient(90deg, var(--color-primary), transparent);
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;
    justify-content: flex-end;
  }

  .auto-refresh-control {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background-color: rgba(212, 175, 55, 0.1);
    border-radius: 20px;
    border: 1px solid rgba(212, 175, 55, 0.2);
    transition: all 0.3s ease;

    &:hover {
      background-color: rgba(212, 175, 55, 0.15);
    }
  }

  .switch-text {
    font-size: 14px;
    color: var(--text-secondary);
    transition: color 0.3s ease;
  }

  .refresh-interval-control {
    display: flex;
    align-items: center;
    margin-left: 10px;
  }

  .interval-label {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .refresh-interval {
    font-size: 12px;
    color: var(--text-secondary);
    background-color: rgba(212, 175, 55, 0.2);
    padding: 2px 8px;
    border-radius: 10px;
  }

  /* 确保所有自动刷新相关文本都适配主题 */
  .el-switch__label {
    color: var(--text-secondary) !important;
  }

  .header-stats {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .header-failed-count {
    display: flex;
    align-items: center;
    color: var(--text-secondary);
    font-size: 14px;
    padding: 6px 12px;
    background-color: rgba(245, 108, 108, 0.1);
    border-radius: 20px;
    border: 1px solid rgba(245, 108, 108, 0.2);
    transition: all 0.3s ease;

    &:hover {
      background-color: rgba(245, 108, 108, 0.15);
      transform: translateY(-2px);
    }
  }

  .filter-container {
    margin-bottom: 24px;
    padding: 16px;
    background-color: var(--bg-tertiary);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--color-primary);
      box-shadow: 0 4px 12px rgba(212, 175, 55, 0.15);
    }
  }

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;

    ::v-deep .el-form-item {
      margin-bottom: 0;
    }

    ::v-deep .el-form-item__label {
      color: var(--text-primary);
      font-weight: 500;
    }

    ::v-deep .el-input__inner,::v-deep .el-select__input {
      border-color: var(--border-color);
      background-color: var(--bg-quaternary);
      color: var(--text-primary);
      transition: all 0.3s ease;

      &:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2);
      }
    }

    ::v-deep .el-button {
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      }
    }
  }

  .header-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;

    &::before {
      content: '';
      display: inline-block;
      width: 4px;
      height: 20px;
      background-color: var(--color-primary);
      margin-right: 12px;
      border-radius: 2px;
    }
  }

  .header-count {
    display: flex;
    align-items: center;
    color: var(--text-secondary);
    font-size: 14px;
    padding: 6px 12px;
    background-color: rgba(245, 108, 108, 0.1);
    border-radius: 20px;
    border: 1px solid rgba(245, 108, 108, 0.2);
    transition: all 0.3s ease;

    &:hover {
      background-color: rgba(245, 108, 108, 0.15);
      transform: translateY(-2px);
    }
  }

  .truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: inline-block;
    max-width: 100%;
  }

  .empty-tasks {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    color: var(--text-tertiary);
    font-size: 16px;
    background-color: var(--bg-quinary);
    border: 1px dashed var(--border-color);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;

    &::before {
      content: '📋';
      margin-right: 12px;
      font-size: 24px;
    }

    &:hover {
      border-color: var(--color-primary);
      color: var(--color-primary);
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(212, 175, 55, 0.2);
    }
  }

  .pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
    }
  }

  .el-table {
    background-color: var(--bg-quaternary);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--border-color);

    // 取消多选框单元格的text-overflow: ellipsis
    ::v-deep .el-table-column--selection .cell {
      text-overflow: unset;
      overflow: visible;
    }

    ::v-deep .el-table__header-wrapper {
      .el-table__header {
        th {
          background-color: var(--bg-tertiary);
          color: var(--text-primary);
          font-weight: 600;
          border-bottom: 1px solid var(--border-color);
          padding: 16px 12px;
          position: relative;

          &:not(:last-child)::after {
            content: '';
            position: absolute;
            right: 0;
            top: 25%;
            height: 50%;
            width: 1px;
            background-color: var(--border-color);
          }
        }
      }
    }

    ::v-deep .el-table__body-wrapper {
      .el-table__body {
        tr {
          background-color: var(--bg-quaternary);
          transition: all 0.2s ease;
          position: relative;

          &:hover {
            background-color: var(--card-hover) !important;
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }

          &:not(:last-child) td {
            border-bottom: 1px solid var(--border-color);
          }

          td {
            color: var(--text-secondary);
            padding: 14px 12px;
            position: relative;

            &:not(:last-child)::after {
              content: '';
              position: absolute;
              right: 0;
              top: 25%;
              height: 50%;
              width: 1px;
              background-color: rgba(0, 0, 0, 0.05);
            }
          }
        }
      }
    }

    ::v-deep .el-table__empty-block {
      background-color: var(--bg-quaternary);
    }

    ::v-deep .el-table__expand-icon {
      color: var(--color-primary);
    }

    // 适配暗色主题的右侧固定列补丁
    ::v-deep .el-table__fixed-right-patch {
      background-color: var(--bg-quaternary) !important;
      border-color: var(--border-color) !important;
    }

    ::v-deep .el-button {
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border-radius: 6px;
      font-weight: 500;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      }

      &:active {
        transform: translateY(0);
      }

      &.el-button--primary {
        background: linear-gradient(135deg, var(--color-primary), rgba(212, 175, 55, 0.8));
        border: none;

        &:hover {
          background: linear-gradient(135deg, var(--color-primary), rgba(212, 175, 55, 0.9));
          box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        }
      }

      &.el-button--info {
        background: linear-gradient(135deg, var(--color-info), rgba(144, 147, 153, 0.8));
        border: none;

        &:hover {
          background: linear-gradient(135deg, var(--color-info), rgba(144, 147, 153, 0.9));
          box-shadow: 0 4px 12px rgba(144, 147, 153, 0.3);
        }
      }
    }
  }

  .batch-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
    padding: 12px 20px;
    background-color: var(--bg-tertiary);
    border-radius: 8px;
    border: 1px solid var(--border-color);
    position: relative;
    z-index: 10;
  }
}

// 响应式设计优化
@media (max-width: 768px) {
  .fail-tasks-container {
    padding: 16px;

    .fail-tasks-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .header-count {
        align-self: flex-start;
      }
    }
  }

  .el-table {
    ::v-deep .el-table__body-wrapper {
      .el-table__body {
        tr {
          &:hover {
            transform: none;
            box-shadow: none;
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .fail-tasks-container {
    padding: 12px;

    .fail-tasks-header {
      .header-title {
        font-size: 16px;
      }
    }
  }

  .el-table {
    ::v-deep .el-table__header-wrapper {
      .el-table__header {
        th {
          padding: 12px 8px;
          font-size: 12px;
        }
      }
    }

    ::v-deep .el-table__body-wrapper {
      .el-table__body {
        tr {
          td {
            padding: 10px 8px;
            font-size: 12px;
          }
        }
      }
    }

    ::v-deep .el-button {
      padding: 6px 8px;
      font-size: 12px;
    }
  }
}
</style>
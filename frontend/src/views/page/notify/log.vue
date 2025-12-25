<template>
	<div class="notify-log">
		<div class="loading-box content-none-data" v-loading="loading" v-if="loading">加载中</div>
		<div v-else class="log-container">
			<div class="log-header">
				<div class="log-title">
					<el-button type="primary" size="small" @click="goToConfig">返回通知配置</el-button>
					<h2>消息记录管理</h2>
				</div>
				<div class="log-actions">
					<el-button type="primary" size="small" @click="exportLog">导出记录</el-button>
					<el-button type="success" size="small" @click="resendSelected" :disabled="selectedRows.length === 0">重新发送</el-button>
					<el-button type="danger" size="small" @click="deleteSelected" :disabled="selectedRows.length === 0">删除记录</el-button>
				</div>
			</div>
			
			<!-- 搜索筛选栏 -->
			<el-card shadow="never" class="search-card">
				<el-form :inline="true" :model="searchForm" class="demo-form-inline">
					<el-form-item label="消息类型">
						<el-input v-model="searchForm.message_type" placeholder="请输入消息类型" size="small"></el-input>
					</el-form-item>
					
					<el-form-item label="通知方式">
						<el-select v-model="searchForm.notify_id" placeholder="请选择通知方式" size="small">
							<el-option label="全部" value=""></el-option>
							<el-option v-for="notify in notifyList" :key="notify.id" :label="notify.method | notifyMethodFilter" :value="notify.id"></el-option>
						</el-select>
					</el-form-item>
					
					<el-form-item label="状态">
						<el-select v-model="searchForm.status" placeholder="请选择状态" size="small">
							<el-option label="全部" value=""></el-option>
							<el-option label="成功" :value="1"></el-option>
							<el-option label="失败" :value="0"></el-option>
						</el-select>
					</el-form-item>
					
					<el-form-item label="时间范围">
						<el-date-picker
							v-model="dateRange"
							type="datetimerange"
							range-separator="至"
							start-placeholder="开始时间"
							end-placeholder="结束时间"
							size="small"
							@change="onDateRangeChange"
						></el-date-picker>
					</el-form-item>
					
					<el-form-item label="关键词">
						<el-input v-model="searchForm.keyword" placeholder="标题或内容" size="small"></el-input>
					</el-form-item>
					
					<el-form-item>
						<el-button type="primary" size="small" @click="search">搜索</el-button>
						<el-button size="small" @click="resetSearch">重置</el-button>
					</el-form-item>
				</el-form>
			</el-card>
			
			<!-- 消息记录列表 -->
			<el-card shadow="never" class="log-table-card">
				<el-table
				v-loading="tableLoading"
				:data="tableData"
				class="log-table"
				@selection-change="handleSelectionChange"
				border
			>
					<el-table-column type="selection" width="55" align="center"></el-table-column>
					<el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
					<el-table-column prop="notify_id" label="通知方式" width="120" align="center">
						<template slot-scope="scope">
							{{ getNotifyMethod(scope.row.notify_id) }}
						</template>
					</el-table-column>
					<el-table-column prop="message_type" label="消息类型" width="120" align="center"></el-table-column>
					<el-table-column prop="title" label="标题" min-width="150"></el-table-column>
					<el-table-column prop="content" label="内容" min-width="200" :show-overflow-tooltip="true"></el-table-column>
					<el-table-column prop="send_time" label="发送时间" width="180" align="center">
						<template slot-scope="scope">
							{{ formatDateTime(scope.row.send_time) }}
						</template>
					</el-table-column>
					<el-table-column prop="status" label="状态" width="100" align="center">
						<template slot-scope="scope">
							<el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
								{{ scope.row.status === 1 ? '成功' : '失败' }}
							</el-tag>
						</template>
					</el-table-column>
					<el-table-column prop="message" label="状态消息" min-width="150" :show-overflow-tooltip="true"></el-table-column>
					<el-table-column label="操作" width="150" align="center">
						<template slot-scope="scope">
							<el-button type="primary" size="mini" @click="resendLog(scope.row.id)">重新发送</el-button>
							<el-button type="danger" size="mini" @click="deleteLog(scope.row.id)">删除</el-button>
						</template>
					</el-table-column>
				</el-table>
				
				<!-- 分页 -->
				<div class="pagination-container">
					<el-pagination
						background
						layout="total, sizes, prev, pager, next, jumper"
						:total="total"
						:page-sizes="[10, 20, 50, 100]"
						:page-size="pageSize"
						:current-page="currentPage"
						@size-change="handleSizeChange"
						@current-change="handleCurrentChange"
					></el-pagination>
				</div>
			</el-card>
			
			<!-- 无数据提示 -->
			<el-empty description="暂无消息记录" v-if="tableData.length === 0 && !tableLoading"></el-empty>
		</div>
	</div>
</template>

<script>
	import { getNotifyList, getNotifyLogList, deleteNotifyLog, resendNotify, batchResendNotify, exportNotifyLog } from '@/api/notify';
	import { exportCsv } from '@/utils/utils';
	export default {
		name: 'NotifyLog',
		components: {},
		data() {
			return {
				loading: false,
				tableLoading: false,
				dataList: [],
				tableData: [],
				total: 0,
				currentPage: 1,
				pageSize: 20,
				searchForm: {
					message_type: '',
					notify_id: '',
					status: '',
					keyword: ''
				},
				dateRange: [],
				start_time: '',
				end_time: '',
				notifyList: [],
				selectedRows: [],
				resendLoading: false
			};
		},
		created() {
			this.getData();
			this.getNotifyConfigList();
		},
		methods: {
			// 返回通知配置页面
			goToConfig() {
				this.$router.push('/notify');
			},
			// 获取通知配置列表
			getNotifyConfigList() {
				getNotifyList().then(res => {
					this.notifyList = res.data;
				}).catch(err => {
					console.error('获取通知配置失败', err);
				});
			},
			
			// 获取消息记录列表
			getData() {
				this.tableLoading = true;
				const params = {
					log: true,
					pageNum: this.currentPage,
					pageSize: this.pageSize,
					message_type: this.searchForm.message_type,
					notify_id: this.searchForm.notify_id || undefined,
					status: this.searchForm.status || undefined,
					keyword: this.searchForm.keyword,
					start_time: this.start_time || undefined,
					end_time: this.end_time || undefined
				};
				
				getNotifyLogList(params).then(res => {
					this.tableLoading = false;
					this.tableData = res.data.dataList;
					this.total = res.data.count;
				}).catch(err => {
					this.tableLoading = false;
					console.error('获取消息记录失败', err);
				});
			},
			
			// 格式化时间
			formatDateTime(timestamp) {
				if (!timestamp) return '';
				const date = new Date(timestamp * 1000);
				return date.toLocaleString('zh-CN', {
					year: 'numeric',
					month: '2-digit',
					day: '2-digit',
					hour: '2-digit',
					minute: '2-digit',
					second: '2-digit'
				});
			},
			
			// 获取通知方式名称
			getNotifyMethod(notifyId) {
				const notify = this.notifyList.find(item => item.id === notifyId);
				return notify ? (notify.method | this.$options.filters.notifyMethodFilter) : '';
			},
			
			// 搜索
			search() {
				this.currentPage = 1;
				this.getData();
			},
			
			// 重置搜索
			resetSearch() {
				this.searchForm = {
					message_type: '',
					notify_id: '',
					status: '',
					keyword: ''
				};
				this.dateRange = [];
				this.start_time = '';
				this.end_time = '';
				this.currentPage = 1;
				this.getData();
			},
			
			// 日期范围变化
			onDateRangeChange(val) {
				if (val && val.length === 2) {
					this.start_time = Math.floor(val[0].getTime() / 1000);
					this.end_time = Math.floor(val[1].getTime() / 1000);
				} else {
					this.start_time = '';
					this.end_time = '';
				}
			},
			
			// 分页大小变化
			handleSizeChange(val) {
				this.pageSize = val;
				this.currentPage = 1;
				this.getData();
			},
			
			// 当前页变化
			handleCurrentChange(val) {
				this.currentPage = val;
				this.getData();
			},
			
			// 选择行变化
			handleSelectionChange(val) {
				this.selectedRows = val;
			},
			
			// 删除单条记录
			deleteLog(id) {
				this.$confirm('确定要删除这条消息记录吗？', '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					this.tableLoading = true;
					deleteNotifyLog([id]).then(res => {
						this.tableLoading = false;
						this.$message({
							message: '删除成功',
							type: 'success'
						});
						this.getData();
					}).catch(err => {
						this.tableLoading = false;
						this.$message.error('删除失败');
					});
				});
			},
			
			// 删除选中记录
			deleteSelected() {
				this.$confirm(`确定要删除选中的${this.selectedRows.length}条消息记录吗？`, '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					const ids = this.selectedRows.map(row => row.id);
					this.tableLoading = true;
					deleteNotifyLog(ids).then(res => {
						this.tableLoading = false;
						this.$message({
							message: '删除成功',
							type: 'success'
						});
						this.selectedRows = [];
						this.getData();
					}).catch(err => {
						this.tableLoading = false;
						this.$message.error('删除失败');
					});
				});
			},
			
			// 重新发送单条通知
			resendLog(id) {
				this.resendLoading = true;
				resendNotify(id).then(res => {
					this.resendLoading = false;
					this.$message({
						message: '重新发送成功',
						type: 'success'
					});
					this.getData();
				}).catch(err => {
					this.resendLoading = false;
					this.$message.error('重新发送失败');
				});
			},
			
			// 重新发送选中通知
			resendSelected() {
				this.$confirm(`确定要重新发送选中的${this.selectedRows.length}条通知吗？`, '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					const ids = this.selectedRows.map(row => row.id);
					this.resendLoading = true;
					batchResendNotify(ids).then(res => {
						this.resendLoading = false;
						this.$message({
							message: `重新发送完成，成功${res.data.success}条，失败${res.data.fail}条`,
							type: 'success'
						});
						this.getData();
					}).catch(err => {
						this.resendLoading = false;
						this.$message.error('重新发送失败');
					});
				});
			},
			
			// 导出记录
			exportLog() {
				this.$confirm('确定要导出当前筛选条件下的所有消息记录吗？', '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'info'
				}).then(() => {
					this.loading = true;
					// 构造导出参数
					const params = {
						export: true,
						message_type: this.searchForm.message_type,
						notify_id: this.searchForm.notify_id || undefined,
						status: this.searchForm.status || undefined,
						keyword: this.searchForm.keyword,
						start_time: this.start_time || undefined,
						end_time: this.end_time || undefined
					};
					
					// 调用API获取所有消息记录
					exportNotifyLog(params).then(res => {
						this.loading = false;
						const data = res.data;
						if (data && data.length > 0) {
							// 定义导出列配置
							const columns = [
								{ title: 'ID', key: 'id' },
								{ title: '通知方式', key: 'notify_id', formatter: (row) => this.getNotifyMethod(row.notify_id) },
								{ title: '消息类型', key: 'message_type' },
								{ title: '标题', key: 'title' },
								{ title: '内容', key: 'content' },
								{ title: '发送时间', key: 'send_time', formatter: (row) => this.formatDateTime(row.send_time) },
								{ title: '状态', key: 'status', formatter: (row) => row.status === 1 ? '成功' : '失败' },
								{ title: '状态消息', key: 'message' },
								{ title: '设备信息', key: 'device_info' }
							];
							
							// 格式化数据
							const formattedData = data.map(row => {
								return {
									id: row.id,
									notify_id: this.getNotifyMethod(row.notify_id),
									message_type: row.message_type,
									title: row.title,
									content: row.content,
									send_time: this.formatDateTime(row.send_time),
									status: row.status === 1 ? '成功' : '失败',
									message: row.message,
									device_info: row.device_info
								};
							});
							
							// 导出CSV文件
							exportCsv(formattedData, '消息记录', [
								{ title: 'ID', key: 'id' },
								{ title: '通知方式', key: 'notify_id' },
								{ title: '消息类型', key: 'message_type' },
								{ title: '标题', key: 'title' },
								{ title: '内容', key: 'content' },
								{ title: '发送时间', key: 'send_time' },
								{ title: '状态', key: 'status' },
								{ title: '状态消息', key: 'message' },
								{ title: '设备信息', key: 'device_info' }
							]);
							
							this.$message({
								message: '导出成功',
								type: 'success'
							});
						} else {
							this.$message.warning('没有数据可以导出');
						}
					}).catch(err => {
						this.loading = false;
						this.$message.error('导出失败');
					});
				});
			}
		}
	}
</script>

<style lang="scss">
	.notify-log {
		box-sizing: border-box;
		width: 100%;
		height: 100%;
		padding: 16px;
		background-color: var(--bg-primary);
		color: var(--text-primary);
		
		.log-container {
			width: 100%;
			background-color: var(--bg-primary);
		}
		
		.log-header {
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 16px;
			
			.log-title {
				display: flex;
				align-items: center;
				gap: 16px;
				
				h2 {
					margin: 0;
					font-size: 20px;
					font-weight: bold;
					color: var(--text-primary);
				}
			}
			
			.log-actions {
				display: flex;
				gap: 8px;
			}
		}
		
		.search-card {
			margin-bottom: 16px;
			background-color: var(--bg-quaternary);
			border: 1px solid var(--border-light);
		}
		
		.log-table-card {
			background-color: var(--bg-quaternary);
			border: 1px solid var(--border-light);
		}
		
		.pagination-container {
			margin-top: 16px;
			display: flex;
			justify-content: flex-end;
		}
		
		:deep(.el-card__body) {
			padding: 16px;
			background-color: var(--bg-quaternary);
		}
		
		// 修复表格整体样式
		:deep(.el-table) {
			background-color: var(--bg-quaternary) !important;
			
			// 移除默认的斑马纹
			&.el-table--striped {
				.el-table__body {
					tr {
						background-color: var(--bg-quaternary) !important;
						
						&.el-table__row--striped {
							background-color: var(--bg-quaternary) !important;
							
							&:hover {
								background-color: var(--card-hover) !important;
							}
						}
						
						&:hover {
							background-color: var(--card-hover) !important;
						}
					}
				}
			}
		}
		
		:deep(.el-table__header-wrapper) {
			background-color: var(--bg-tertiary);
			
			th {
				background-color: var(--bg-tertiary);
				color: var(--text-primary);
				border-bottom: 1px solid var(--border-color);
			}
		}
		
		:deep(.el-table__body-wrapper) {
			tr {
				background-color: var(--bg-quaternary) !important;
				color: var(--text-primary);
				
				&:hover {
					background-color: var(--card-hover) !important;
				}
				
				td {
					border-bottom: 1px solid var(--border-color);
					color: var(--text-primary);
				}
				
				// 确保斑马纹行也使用深色背景
				&.el-table__row--striped {
					background-color: var(--bg-quaternary) !important;
					
					&:hover {
						background-color: var(--card-hover) !important;
					}
				}
			}
		}
		

		
		:deep(.el-pagination) {
			background-color: var(--bg-quaternary);
			color: var(--text-primary);
			
			button {
				background-color: var(--bg-quaternary);
				color: var(--text-primary);
				border-color: var(--border-color);
				
				&:hover {
					background-color: var(--card-hover);
					color: var(--color-primary);
				}
			}
			
			.is-active {
				background-color: var(--color-primary);
				color: white;
			}
		}
		
		// 表单元素深色模式适配
		:deep(.el-form-item__label) {
			color: var(--text-primary);
		}
		
		:deep(.el-input__inner) {
			background-color: var(--bg-tertiary);
			color: var(--text-primary);
			border-color: var(--border-color);
			
			&:focus {
				border-color: var(--color-primary);
				box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2);
			}
			
			&::placeholder {
				color: var(--text-tertiary);
			}
		}
		
		:deep(.el-select) {
			.el-input__inner {
				background-color: var(--bg-tertiary);
				color: var(--text-primary);
				border-color: var(--border-color);
			}
		}
		
		:deep(.el-select-dropdown) {
			background-color: var(--bg-quaternary);
			border: 1px solid var(--border-light);
			box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
			
			.el-select-dropdown__item {
				color: var(--text-primary);
				
				&:hover {
					background-color: var(--card-hover);
				}
				
				&.selected {
					background-color: var(--card-hover);
					color: var(--color-primary);
				}
			}
			
			.el-select-dropdown__empty {
				color: var(--text-tertiary);
			}
		}
		
		// 按钮深色模式适配
		:deep(.el-button) {
			&.el-button--primary {
				background-color: var(--color-primary);
				border-color: var(--color-primary);
				color: white;
				
				&:hover {
					background-color: var(--color-primary);
					border-color: var(--color-primary);
					opacity: 0.9;
				}
			}
			
			&.el-button--success {
				background-color: var(--color-success);
				border-color: var(--color-success);
				color: white;
			}
			
			&.el-button--danger {
				background-color: var(--color-danger);
				border-color: var(--color-danger);
				color: white;
			}
			
			&.el-button--default {
				background-color: var(--bg-tertiary);
				border-color: var(--border-color);
				color: var(--text-primary);
				
				&:hover {
					background-color: var(--card-hover);
					border-color: var(--color-primary);
					color: var(--color-primary);
				}
			}
		}
		
		// 分页控件深色模式适配
		:deep(.el-pagination) {
			background-color: var(--bg-quaternary);
			color: var(--text-primary);
			
			button {
				background-color: var(--bg-tertiary);
				color: var(--text-primary);
				border-color: var(--border-color);
				
				&:hover {
					background-color: var(--card-hover);
					border-color: var(--color-primary);
					color: var(--color-primary);
				}
			}
			
			.is-active {
				background-color: var(--color-primary);
				border-color: var(--color-primary);
				color: white;
			}
			
			.el-pagination__total {
				color: var(--text-primary);
			}
			
			.el-pagination__sizes {
				select {
					background-color: var(--bg-tertiary);
					color: var(--text-primary);
					border-color: var(--border-color);
				}
			}
		}
		
		// 状态标签深色模式适配
		:deep(.el-tag) {
			&.el-tag--success {
				background-color: rgba(103, 194, 58, 0.2);
				color: var(--color-success);
				border: 1px solid var(--color-success);
			}
			
			&.el-tag--danger {
				background-color: rgba(245, 108, 108, 0.2);
				color: var(--color-danger);
				border: 1px solid var(--color-danger);
			}
		}
		
		// 滚动条深色模式适配
		:deep(.el-table__body-wrapper) {
			&::-webkit-scrollbar {
				width: 8px;
				height: 8px;
			}
			
			&::-webkit-scrollbar-track {
				background-color: var(--bg-quinary);
			}
			
			&::-webkit-scrollbar-thumb {
				background-color: var(--border-light);
				border-radius: 4px;
				
				&:hover {
					background-color: var(--color-primary);
				}
			}
		}
		
		// 日期选择器深色模式适配
		:deep(.el-date-editor) {
			.el-input__inner {
				background-color: var(--bg-tertiary);
				color: var(--text-primary);
			}
		}
		
		:deep(.el-picker-panel) {
			background-color: var(--bg-quaternary);
			border: 1px solid var(--border-light);
			
			.el-date-table th {
				color: var(--text-primary);
				background-color: var(--bg-tertiary);
			}
			
			.el-date-table td {
				color: var(--text-primary);
				background-color: var(--bg-quaternary);
				
				&.today {
					color: var(--color-primary);
					background-color: var(--bg-quaternary);
				}
				
				&.current {
					color: var(--color-primary);
					background-color: var(--bg-quaternary);
				}
				
				.el-date-table__row:hover td {
					background-color: var(--card-hover) !important;
				}
			}
			
			.el-month-table th,
			.el-year-table th {
				color: var(--text-primary);
				background-color: var(--bg-tertiary);
			}
			
			.el-month-table td,
			.el-year-table td {
				color: var(--text-primary);
				background-color: var(--bg-quaternary);
				
				&:hover {
					background-color: var(--card-hover) !important;
				}
				
				&.current {
					color: var(--color-primary);
					background-color: var(--bg-quaternary);
				}
			}
			
			.el-picker-panel__footer {
				background-color: var(--bg-tertiary);
				border-top: 1px solid var(--border-color);
				
				button {
					background-color: var(--bg-quaternary);
					color: var(--text-primary);
					border-color: var(--border-color);
					
					&:hover {
						background-color: var(--card-hover);
						color: var(--color-primary);
					}
				}
			}
			
			// 修复日期选择器头部背景色
			.el-picker-panel__header {
				background-color: var(--bg-tertiary);
				
				.btn-prev,
				.btn-next {
					color: var(--text-primary);
					
					&:hover {
						color: var(--color-primary);
					}
				}
				
				.el-year-btn,
				.el-month-btn {
					color: var(--text-primary);
					
					&:hover {
						color: var(--color-primary);
					}
				}
			}
		}
		

		
		// 空状态提示深色模式适配
		:deep(.el-empty) {
			color: var(--text-tertiary);
			
			.el-empty__image {
				filter: brightness(0.7);
			}
			
			.el-empty__description {
				color: var(--text-tertiary);
			}
		}
		
		// 按钮深色模式适配
		:deep(.el-button) {
			&.el-button--primary {
				background-color: var(--color-primary);
				border-color: var(--color-primary);
			}
			
			&.el-button--success {
				background-color: var(--color-success);
				border-color: var(--color-success);
			}
			
			&.el-button--danger {
				background-color: var(--color-danger);
				border-color: var(--color-danger);
			}
		}
		
		// 标签深色模式适配
		:deep(.el-tag) {
			&.el-tag--success {
				background-color: rgba(103, 194, 58, 0.2);
				color: var(--color-success);
				border: 1px solid var(--color-success);
			}
			
			&.el-tag--danger {
				background-color: rgba(245, 108, 108, 0.2);
				color: var(--color-danger);
				border: 1px solid var(--color-danger);
			}
		}
		
		.log-table {
			width: 100%;
		}
	}
</style>
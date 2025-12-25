<template>
	<div class="pathSelect">
		<el-dialog top="8vh" :close-on-click-modal="false" :visible.sync="dialogShow" title="选择目录" width="90%" max-width="520px"
			:before-close="closeShow" :append-to-body="true">
      <el-input
          placeholder="输入关键字进行过滤"
          v-model="filterText">
      </el-input>
			<div class="tree-container">
        <el-tree :props="props" :load="loadNode" :filter-node-method="filterNode" lazy :highlight-current="true" :check-on-click-node="true"
                 @node-click="nodeClick" v-if="dialogShow" :expand-on-click-node="false" ref="tree">
        </el-tree>
      </div>
			<span slot="footer" class="dialog-footer">
				<el-button @click="closeShow">取 消</el-button>
				<el-button type="primary" @click="submit" :loading="submitLoading"
					:disabled="cuPath == null">{{cuPath == null ? '请先选择路径' : '确 定'}}</el-button>
			</span>
		</el-dialog>
	</div>
</template>

<script>
	import {
		alistGetPath
	} from "@/api/job";
	export default {
		name: 'PathSelect',
		components: {},
		props: {
			alistId: {
				type: Number,
				default: null
			}
		},
		data() {
			return {
				dialogShow: false,
				pathLoading: false,
				submitLoading: false,
				cuPath: null,
        filterText: '',
				props: {
					label: 'path',
					children: 'child',
					isLeaf: 'leaf'
				}
			};
		},
		created() {},
		beforeDestroy() {},
    watch: {
      filterText(val) {
        this.$refs.tree.filter(val);
      }
    },
		methods: {
			show() {
				this.dialogShow = true;
			},
			async getPath(path) {
				this.pathLoading = true;
				try {
					let res = await alistGetPath(this.alistId, path);
					this.pathLoading = false;
					return res.data;
				} catch (err) {
					return [];
					this.pathLoading = false;
				}
			},
			async loadNode(node, resolve) {
				let path = '/';
				let cup = node;
				for (let i = 0; i < node.level; i++) {
					path = '/' + cup.data.path + path;
					cup = cup.parent;
				}
				return resolve(await this.getPath(path));
			},
			closeShow() {
				this.dialogShow = false;
				this.cuPath = null;
				// 重置树的选中状态
				if (this.$refs.tree) {
					this.$refs.tree.setCurrentKey(null);
				}
			},
			nodeClick(dt, node, se) {
				let path = '/';
				let cup = node;
				for (let i = 0; i < node.level; i++) {
					path = '/' + cup.data.path + path;
					cup = cup.parent;
				}
				this.cuPath = path;
				// 确保节点被正确选中
				if (this.$refs.tree) {
					this.$refs.tree.setCurrentKey(node.key);
				}
			},
			submit() {
				this.$emit('submit', this.cuPath);
				this.closeShow();
			},
      filterNode(value, data) {
        if (!value) return true;
        return data.path.indexOf(value) !== -1;
      }
		}
	}
</script>

<style lang="scss" scoped>
	.pathSelect {
		/* 树形组件自定义样式 */
		.el-tree {
			background: var(--bg-tertiary);
			border: 1px solid var(--border-light);
			color: var(--text-primary);
			
			/* 确保树节点内容有足够的内边距 */
			.el-tree-node__content {
				padding: 8px 16px;
				transition: all 0.3s ease;
				position: relative;
				background: transparent;
				color: var(--text-primary);
			}
			
			/* 高亮当前选中节点 - 使用主题变量 */
			:deep(.el-tree-node.is-current > .el-tree-node__content) {
				background-color: rgba(212, 175, 55, 0.2) !important;
				color: var(--color-primary) !important;
				font-weight: 700 !important;
				border-radius: 6px !important;
				box-shadow: 0 4px 16px rgba(212, 175, 55, 0.3) !important;
				transition: all 0.3s ease !important;
				border-left: 4px solid var(--color-primary) !important;
				padding-left: 12px !important;
				outline: 1px solid rgba(212, 175, 55, 0.5) !important;
				outline-offset: -1px !important;
			}
			
			/* 确保选中状态在悬停时也保持 */
			:deep(.el-tree-node.is-current > .el-tree-node__content:hover) {
				background-color: rgba(212, 175, 55, 0.3) !important;
				color: var(--color-primary) !important;
				box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4) !important;
			}
			
			/* 鼠标悬停效果 */
			.el-tree-node__content:hover {
				background-color: var(--tree-hover);
				border-radius: 6px;
				transition: all 0.3s ease;
			}
			
			/* 确保选中状态在展开/折叠图标上也有效果 */
			:deep(.el-tree-node.is-current > .el-tree-node__content .el-tree-node__expand-icon) {
				color: var(--color-primary) !important;
			}
			
			/* 确保选中状态在节点文本上也有效果 */
			:deep(.el-tree-node.is-current > .el-tree-node__content .el-tree-node__label) {
				color: var(--color-primary) !important;
				font-weight: 700 !important;
			}
			
			/* 子节点样式调整 */
			.el-tree-node__children {
				.el-tree-node__content {
					background: transparent;
				}
			}
			
			/* 滚动条样式优化 */
			&::-webkit-scrollbar {
				width: 6px;
				height: 6px;
			}
			
			&::-webkit-scrollbar-track {
				background: var(--bg-quaternary);
				border-radius: 3px;
			}
			
			&::-webkit-scrollbar-thumb {
				background: var(--border-color);
				border-radius: 3px;
			}
			
			&::-webkit-scrollbar-thumb:hover {
				background: var(--text-tertiary);
			}
		}
		
		/* 输入框样式优化 */
		.el-input {
			margin-bottom: 16px;
			
			.el-input__inner {
				border-radius: 4px;
				transition: all 0.3s ease;
				background-color: var(--bg-tertiary);
				border: 1px solid var(--border-color);
				color: var(--text-primary);
			}
			
			.el-input__inner:focus {
				border-color: var(--color-primary);
				box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2);
			}
			
			.el-input__inner::placeholder {
				color: var(--text-tertiary);
			}
		}
		
		/* 对话框样式优化 */
		.el-dialog {
			background-color: var(--bg-secondary);
			color: var(--text-primary);
		}
		
		.el-dialog__header {
			border-bottom: 1px solid var(--border-color);
		}
		
		.el-dialog__title {
			color: var(--text-primary);
		}
		
		.el-dialog__body {
			padding: 20px;
			background-color: var(--bg-secondary);
		}
		
		.el-dialog__footer {
			border-top: 1px solid var(--border-color);
		}
	}
	
	.tree-container {
		width: 100%;
		max-height: 60vh;
		min-height: 30vh;
		overflow-y: auto;
		background-color: var(--bg-tertiary);
	}
</style>
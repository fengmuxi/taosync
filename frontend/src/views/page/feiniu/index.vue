<template>
	<div class="feiniu">
		<div class="loading-box content-none-data" v-loading="true" v-if="getLoading">加载中</div>
		<div v-else>
			<el-tabs v-model="activeTab" type="border-card" class="tabs-container">
				<el-tab-pane label="飞牛配置" name="config">
					<fei-niu-config></fei-niu-config>
				</el-tab-pane>
				<el-tab-pane label="飞牛刷新任务记录" name="failTasks">
					<fei-niu-fail-tasks></fei-niu-fail-tasks>
				</el-tab-pane>
			</el-tabs>
		</div>
	</div>
</template>

<script>
import FeiNiuConfig from './components/FeiNiuConfig.vue'
import FeiNiuFailTasks from './components/FeiNiuFailTasks.vue'

export default {
	name: 'FeiNiuIndex',
	components: {
		FeiNiuConfig,
		FeiNiuFailTasks
	},
	data() {
			return {
				activeTab: 'config',
				getLoading: false
			};
	},
	created() {
		this.getLoading = false;
	}
}
</script>

<style lang="scss" scoped>
	.feiniu {
		box-sizing: border-box;
		width: 100%;
		height: 100%;
		position: relative;
		overflow: hidden;
		background: var(--bg-primary);

		.loading-box {
			box-sizing: border-box;
			width: 100%;
			height: 100%;
			display: flex;
			align-items: center;
			justify-content: center;
			background: var(--bg-primary);
			position: relative;
			
			&::after {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				bottom: 0;
				background: linear-gradient(45deg, rgba(212, 175, 55, 0.05), rgba(103, 194, 58, 0.05));
				animation: shimmer 2s infinite;
			}
		}
	}

	@keyframes shimmer {
		0% {
			opacity: 0.3;
			transform: translateX(-100%);
		}
		50% {
			opacity: 0.7;
		}
		100% {
			opacity: 0.3;
			transform: translateX(100%);
		}
	}

	@keyframes pulse {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.05);
		}
		100% {
			transform: scale(1);
		}
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.card-box {
		box-sizing: border-box;
		padding: 16px;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
		gap: 24px;
		width: 100%;
		max-width: 100%;
		position: relative;
		z-index: 1;
		margin-top: 16px;

		.card-item {
			background: linear-gradient(145deg, var(--bg-tertiary), var(--bg-quaternary));
			border-radius: 16px;
			border: 1px solid var(--border-color);
			margin: 0;
			padding: 0;
			height: 100%;
			min-height: 220px;
			display: flex;
			flex-direction: column;
			overflow: hidden;
			position: relative;
			z-index: 1;
			transition: all 0.5s cubic-bezier(0.2, 0.6, 0.3, 1);
			box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
			animation: fadeIn 0.6s ease-out;
			animation-fill-mode: both;

			&:nth-child(1) { animation-delay: 0.1s; }
			&:nth-child(2) { animation-delay: 0.2s; }
			&:nth-child(3) { animation-delay: 0.3s; }
			&:nth-child(4) { animation-delay: 0.4s; }
			&:nth-child(5) { animation-delay: 0.5s; }
			&:nth-child(6) { animation-delay: 0.6s; }

			&::before {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				height: 4px;
				background: linear-gradient(90deg, var(--color-primary), var(--color-success));
				opacity: 0;
				transition: opacity 0.4s cubic-bezier(0.2, 0.6, 0.3, 1);
			}

			&:hover::before {
				opacity: 1;
			}

			.card-item-content {
				padding: 24px;
				background: transparent;
				border: none;
				border-radius: 0;
				transition: all 0.4s cubic-bezier(0.2, 0.6, 0.3, 1);
				cursor: pointer;
				position: relative;
				overflow: hidden;
				flex: 1;
				display: flex;
				flex-direction: column;
				min-height: 180px;

				&::after {
					content: '';
					position: absolute;
					top: -50%;
					left: -50%;
					width: 200%;
					height: 200%;
					background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
					opacity: 0;
					transition: opacity 0.4s cubic-bezier(0.2, 0.6, 0.3, 1);
					z-index: 1;
				}

				&:hover::after {
					opacity: 1;
				}

				.card-item-top {
					display: flex;
					align-items: flex-start;
					margin-bottom: 16px;
					position: relative;
					z-index: 2;

					.el-image {
						border-radius: 12px;
						box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
						transition: transform 0.4s cubic-bezier(0.2, 0.6, 0.3, 1), box-shadow 0.4s cubic-bezier(0.2, 0.6, 0.3, 1);
					}

					&:hover .el-image {
						transform: scale(1.08);
						box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
					}
				}

				.card-item-user {
					margin-bottom: 12px;
					max-width: 100%;
					flex-shrink: 0;
					min-height: 48px;

					.card-item-name {
						font-size: 18px;
						font-weight: 600;
						color: var(--text-primary);
						margin-bottom: 6px;
						white-space: nowrap;
						overflow: hidden;
						text-overflow: ellipsis;
						max-width: 100%;
						letter-spacing: 0.5px;
					}

					.card-item-status {
						display: inline-flex;
						align-items: center;
						padding: 4px 12px;
						border-radius: 20px;
						font-size: 12px;
						font-weight: 500;
						margin-top: 6px;
						flex-shrink: 0;
						letter-spacing: 0.5px;

						&::before {
							content: '';
							display: inline-block;
							width: 6px;
							height: 6px;
							border-radius: 50%;
							margin-right: 6px;
						}

						&.enabled {
							background-color: rgba(19, 206, 102, 0.15);
							color: #13ce66;
							border: 1px solid rgba(19, 206, 102, 0.3);
							animation: pulse 2s infinite;

							&::before {
								background-color: #13ce66;
							}
						}

						&.disabled {
							background-color: rgba(144, 147, 153, 0.15);
							color: #909399;
							border: 1px solid rgba(144, 147, 153, 0.3);

							&::before {
								background-color: #909399;
							}
						}
					}
				}

				.card-item-host {
					margin: 12px 0;
					font-size: 14px;
					color: var(--text-secondary);
					white-space: nowrap;
					overflow: hidden;
					text-overflow: ellipsis;
					cursor: pointer;
					flex-shrink: 0;
					min-height: 30px;
					padding: 6px 0;
					border-bottom: 1px dashed var(--border-color);
					transition: color 0.2s ease;

					&:hover {
						color: var(--color-primary);
					}
				}

				.card-item-info {
					margin-top: 12px;
					flex: 1;
					display: flex;
					flex-direction: column;
					justify-content: flex-start;
					min-height: 30px;

					.info-item {
						display: flex;
						justify-content: flex-start;
						align-items: flex-start;
						margin-bottom: 8px;
						font-size: 13px;
						line-height: 1.5;
						min-height: 20px;

						.label {
							color: var(--text-tertiary);
							margin-right: 8px;
							white-space: nowrap;
							min-width: 40px;
						}

						.value {
							color: var(--text-secondary);
							flex: 1;
							white-space: nowrap;
							overflow: hidden;
							text-overflow: ellipsis;
							min-width: 0;

							&.library-id {
								color: var(--color-warning);
							}

							&.remark {
								color: var(--color-info);
							}
						}
						
						&.placeholder {
							visibility: hidden;
							min-height: 20px;
						}
					}
				}
			}

			.card-item-bottom {
				margin-top: auto;
				display: flex;
				justify-content: center;
				gap: 12px;
				align-items: center;
				padding: 16px 24px;
				border-top: 1px solid var(--border-color);
				flex-shrink: 0;
				position: relative;
				z-index: 20;
				background: rgba(0, 0, 0, 0.05);

				.el-button {
						border-radius: 8px;
						font-weight: 500;
						letter-spacing: 0.5px;
						transition: all 0.3s ease;

						&:hover {
							transform: translateY(-2px);
							box-shadow: 0 4px 8px rgba(212, 175, 55, 0.2);
						}
					}
			}
		}

		.card-add {
			font-size: 18px;
			cursor: pointer;
			display: flex;
			justify-content: center;
			align-items: center;
			color: var(--text-tertiary);
			background: linear-gradient(145deg, var(--bg-tertiary), var(--bg-quaternary));
			border: 2px dashed var(--border-color);
			border-radius: 16px;
			min-height: 220px;
			transition: all 0.3s ease;
			position: relative;
			overflow: hidden;
			animation: fadeIn 0.5s ease-out;
			animation-delay: 0.7s;
			animation-fill-mode: both;

			&::before {
				content: '+';
				font-size: 48px;
				font-weight: 300;
				margin-right: 12px;
				opacity: 0.5;
			}

			&:hover {
				border-color: var(--color-primary);
				color: var(--color-primary);
				background: linear-gradient(145deg, var(--bg-tertiary), rgba(212, 175, 55, 0.1));
				transform: translateY(-4px);
				box-shadow: 0 8px 16px rgba(212, 175, 55, 0.2);

				&::before {
					opacity: 1;
				}
			}
		}

		.card-item:hover {
			border-color: var(--color-primary);
			transform: translateY(-8px);
			box-shadow: 0 16px 32px rgba(64, 158, 255, 0.3);
		}
	}

	.tabs-container {
		margin: 8px;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		border: 1px solid var(--border-light);

		::v-deep .el-tabs__header {
			background-color: var(--bg-tertiary);
			margin: 0;
			display: flex;
			align-items: center;
		}

		::v-deep .el-tabs__nav-wrap {
			padding: 0 16px;
		}

		::v-deep .el-tabs__nav {
			display: flex;
			align-items: center;
		}

		::v-deep .el-tabs__item {
			color: var(--text-secondary);
			font-weight: 500;
			padding: 0 20px;
			height: 50px;
			line-height: 50px;
			transition: all 0.3s ease;
			display: flex;
			align-items: center;
			justify-content: center;
			text-align: center;

			&:hover {
				color: var(--color-primary);
			}

			&.is-active {
				color: var(--color-primary);
				font-weight: 600;
			}
		}

		::v-deep .el-tabs__active-bar {
			background-color: var(--color-primary);
			height: 3px;
		}
	}

	.fail-tasks-container {
		padding: 24px;
		background-color: var(--bg-quaternary);
		border-radius: 12px;
		min-height: 500px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
		position: relative;
		overflow: hidden;

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
		border-radius: 12px;
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
			box-shadow: 0 8px 16px rgba(64, 158, 255, 0.1);
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
		overflow: hidden;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
		border: 1px solid var(--border-color);

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

	.elform-box {
		padding: 24px;
		background-color: var(--bg-quaternary);
		border-radius: 12px;
		margin: 16px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

		::v-deep .el-form-item {
			margin-bottom: 24px;
			transition: all 0.3s ease;

			&:hover {
				transform: translateY(-2px);
			}

			.el-form-item__label {
				color: var(--text-primary);
				font-weight: 500;
				font-size: 14px;
				line-height: 40px;
				padding-right: 12px;
			}

			.el-form-item__content {
				line-height: 40px;
				position: relative;
			}

			.el-input {
				.el-input__inner {
					background-color: var(--bg-tertiary);
					border: 1px solid var(--border-color);
					border-radius: 8px;
					color: var(--text-primary);
					font-size: 14px;
					padding: 0 35px 0 40px;
					height: 40px;
					line-height: 40px;
					transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
					box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

					&:focus {
						border-color: var(--color-primary);
						box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
						transform: translateY(-1px);
					}

					&:hover {
						border-color: var(--color-primary);
					}

					&::placeholder {
						color: var(--text-tertiary);
					}
				}

				.el-input__prefix {
					left: 12px;
					color: var(--text-secondary);
					transition: color 0.3s ease;
					display: flex;
					align-items: center;
					justify-content: center;
				}

				&:focus-within .el-input__prefix {
					color: var(--color-primary);
				}
			}
		}

		::v-deep .el-form-item__error {
			color: var(--color-danger);
			font-size: 12px;
			padding-top: 4px;
		}
	}

	.form-tip {
		font-size: 13px;
		color: var(--text-tertiary);
		margin-top: 8px;
		padding: 8px 12px;
		background-color: rgba(212, 175, 55, 0.1);
		border-radius: 8px;
		border-left: 3px solid var(--color-primary);
		transition: all 0.3s ease;

		&:hover {
			background-color: rgba(212, 175, 55, 0.15);
			transform: translateX(2px);
		}
	}

	::v-deep .el-dialog {
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
		animation: dialogFadeIn 0.3s ease-out;

		.el-dialog__header {
			background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-quaternary));
			padding: 20px 24px;
			border-bottom: 1px solid var(--border-color);

			.el-dialog__title {
				color: var(--text-primary);
				font-weight: 600;
				font-size: 18px;
			}

			.el-dialog__close {
				color: var(--text-secondary);
				font-size: 18px;
				transition: all 0.3s ease;

				&:hover {
					color: var(--color-danger);
					transform: rotate(90deg);
				}
			}
		}

		.el-dialog__body {
			padding: 0;
			background-color: var(--bg-quaternary);
		}

		.el-dialog__footer {
			background-color: var(--bg-tertiary);
			padding: 16px 24px;
			border-top: 1px solid var(--border-color);
			text-align: right;

			.el-button {
				border-radius: 8px;
				font-weight: 500;
				padding: 10px 20px;
				transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
				margin-left: 12px;

				&:hover {
					transform: translateY(-2px);
					box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

		@keyframes dialogFadeIn {
			from {
				opacity: 0;
				transform: scale(0.9) translateY(-20px);
			}
			to {
				opacity: 1;
				transform: scale(1) translateY(0);
			}
		}
	}

	// 响应式设计优化 - 修复布局错位问题
	@media (max-width: 1200px) {
		.card-box {
			grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
			gap: 20px;
			padding: 16px;
		}
	}

	@media (max-width: 768px) {
		.tabs-container {
			margin: 8px;
		}

		.card-box {
			grid-template-columns: 1fr;
			padding: 12px;
			gap: 16px;
			margin-top: 12px;
		}

		.card-item {
			min-height: 200px;

			.card-item-content {
				padding: 16px;
				
				.card-item-top {
					flex-direction: row;
					align-items: center;
					text-align: left;

					.el-image {
						margin-bottom: 0;
						margin-right: 16px;
					}
				}
			}

			.card-item-bottom {
				padding: 12px 16px;
				justify-content: center;
				flex-wrap: wrap;
				gap: 8px;

				.el-button {
					flex: 1;
					min-width: 80px;
				}
			}
		}

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

		::v-deep .el-dialog {
			width: 90% !important;
			margin: 5vh auto !important;
		}
	}

	@media (max-width: 480px) {
		.tabs-container {
			margin: 4px;

			::v-deep .el-tabs__nav-wrap {
				padding: 0 8px;
			}

			::v-deep .el-tabs__item {
				padding: 0 12px;
				font-size: 14px;
			}
		}

		.card-box {
			padding: 8px;
			gap: 12px;

			.card-item {
				min-height: 180px;

				.card-item-content {
					padding: 12px;

					.card-item-top {
						flex-direction: column;
						align-items: center;
						text-align: center;

						.el-image {
							margin-right: 0;
							margin-bottom: 12px;
							width: 50px !important;
							height: 50px !important;
						}
					}

					.card-item-user {
						text-align: center;

						.card-item-name {
							font-size: 16px;
						}
					}

					.card-item-host {
						text-align: center;
						font-size: 13px;
					}
				}

				.card-item-bottom {
					flex-direction: column;
					align-items: center;
					gap: 8px;

					.el-button {
						width: 100%;
						max-width: 120px;
					}
				}
			}
		}

		.fail-tasks-container {
			padding: 12px;

			.fail-tasks-header {
				.header-title {
					font-size: 16px;
				}
			}
		}

		::v-deep .el-dialog {
			width: 95% !important;
			margin: 2.5vh auto !important;
		}

		.elform-box {
			padding: 16px;
			margin: 8px;
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
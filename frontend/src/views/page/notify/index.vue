<template>
	<div class="notify">
		<div class="header-box">
			<h2>通知配置</h2>
			<el-button type="primary" @click="goToLog">消息记录</el-button>
		</div>
		<div class="loading-box content-none-data" v-loading="true" v-if="loading">加载中</div>
		<div v-else class="card-box">
			<div class="card-item" v-for="item in dataList">
				<div class="card-item-top">
					<el-image :src="`/notify/${item.method}.png`" fit="contain" class="card-item-logo"></el-image>
					<div class="card-item-info">
						<div class="card-item-user">{{item.method | notifyMethodFilter}}</div>
						<div :class="`card-item-enable enable-${item.enable == 1 ? 'enable' : 'disable'}`">
							{{item.enable == 1 ? '已启用' : '已禁用'}}
						</div>
					</div>
				</div>
				<div class="card-item-bottom">
					<el-button size="small" type="primary" @click="editShowDialog(item)">编辑</el-button>
					<el-button size="small" type="success" v-if="item.enable == 0"
						@click="enableNotify(item.id, 1)">启用</el-button>
					<el-button size="small" type="warning" v-else @click="enableNotify(item.id, 0)">禁用</el-button>
					<el-button size="small" type="primary" :loading="tstLoading" @click="tstCu(item)">测试</el-button>
					<el-button size="small" type="danger" @click="delCu(item.id)">删除</el-button>
				</div>
			</div>
			<div class="card-item card-add" @click="addShow" v-if="!loading">
				<template v-if="dataList.length == 0">
					暂无通知配置，请<span class="highlight-text">新增</span>
				</template>
				<span v-else>新增</span>
			</div>
			<el-dialog :close-on-click-modal="false" top="6vh" :visible.sync="editShow" :title="editFlag ? '编辑' : '新增'"
				width="680px" :before-close="closeShow" :append-to-body="true">
				<div class="elform-box">
					<el-form :model="editData" :rules="editRule[editData.method]" ref="addRule" v-if="editShow"
						label-width="120px">
						<el-form-item prop="enable" label="是否启用">
							<el-switch v-model="editData.enable" :active-value="1" :inactive-value="0">
							</el-switch>
						</el-form-item>
						<el-form-item prop="method" label="方式">
							<el-select v-model="editData.method" @change="methodChange" class="full-width">
									<el-option :key="meItem - 1" :value="meItem - 1" :label="meItem - 1 | notifyMethodFilter"
										v-for="meItem in 4"></el-option>
								</el-select>
						</el-form-item>
						<template v-if="editData.method == 0">
							<el-form-item prop="params.url" label="请求地址">
								<el-input v-model="editData.params.url" placeholder="请输入请求地址"></el-input>
							</el-form-item>
							<el-form-item prop="params.method" label="请求方法">
								<el-select v-model="editData.params.method" class="full-width">
									<el-option key="POST" value="POST" label="POST"></el-option>
									<el-option key="PUT" value="PUT" label="PUT"></el-option>
									<el-option key="GET" value="GET" label="GET"></el-option>
								</el-select>
							</el-form-item>
							<el-form-item v-if="editData.params.method != 'GET'" prop="params.contentType" label="请求体类型">
								<el-select v-model="editData.params.contentType" class="full-width">
									<el-option key="application/json" value="application/json" label="application/json"></el-option>
									<el-option key="application/x-www-form-urlencoded" value="application/x-www-form-urlencoded"
										label="application/x-www-form-urlencoded"></el-option>
								</el-select>
							</el-form-item>
							<el-form-item prop="params.titleName" label="标题参数名">
								<el-input v-model="editData.params.titleName" placeholder="请输入标题参数名"></el-input>
							</el-form-item>
							<el-form-item prop="params.needContent" label="是否需要内容">
								<el-select v-model="editData.params.needContent" class="full-width">
									<el-option :key="true" :value="true" label="需要"></el-option>
									<el-option :key="false" :value="false" label="不需要"></el-option>
								</el-select>
							</el-form-item>
							<el-form-item prop="params.contentName" v-if="editData.params.needContent" label="内容参数名">
								<el-input v-model="editData.params.contentName" placeholder="请输入内容参数名"></el-input>
							</el-form-item>
						</template>
						<template v-else-if="editData.method == 1">
							<div class="tip-box">同时支持 <a href="https://sct.ftqq.com/r/15503" target="_blank">Server酱ᵀ</a>(免费5次/天)
								与 <a href="https://sc3.ft07.com/" target="_blank">Server酱³</a>(公测不限次)</div>
							<el-form-item prop="params.sendKey" label="SendKey">
								<el-input v-model="editData.params.sendKey" placeholder="请输入SendKey"></el-input>
							</el-form-item>
						</template>
						<template v-else-if="editData.method == 2">
							<div class="tip-box"><a
									href="https://open.dingtalk.com/document/orgapp/custom-bot-creation-and-installation"
									target="_blank">配置指南</a> 安全设置请采用[自定义关键字]，关键字内容为[TaoSync]，不含中括号</div>
							<el-form-item prop="params.url" label="WebHook">
								<el-input v-model="editData.params.url"
									placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxxx"></el-input>
							</el-form-item>
							<el-form-item prop="params.isAtAll" label="是否@所有人">
								<el-select v-model="editData.params.isAtAll" class="full-width">
									<el-option :key="true" :value="true" label="是"></el-option>
									<el-option :key="false" :value="false" label="否"></el-option>
								</el-select>
							</el-form-item>
						</template>
						<template v-else-if="editData.method == 3">
							<div class="tip-box">邮件通知配置指南：请填写SMTP服务器信息，支持SSL/TLS加密</div>
							<el-form-item prop="params.smtpHost" label="SMTP服务器">
								<el-input v-model="editData.params.smtpHost" placeholder="smtp.example.com"></el-input>
							</el-form-item>
							<el-form-item prop="params.smtpPort" label="SMTP端口">
								<el-input v-model="editData.params.smtpPort" placeholder="587"></el-input>
							</el-form-item>
							<el-form-item prop="params.smtpSecure" label="是否启用SSL/TLS">
								<el-select v-model="editData.params.smtpSecure" class="full-width">
									<el-option :key="true" :value="true" label="是"></el-option>
									<el-option :key="false" :value="false" label="否"></el-option>
								</el-select>
							</el-form-item>
							<el-form-item prop="params.smtpUser" label="邮箱账号">
								<el-input v-model="editData.params.smtpUser" placeholder="your-email@example.com"></el-input>
							</el-form-item>
							<el-form-item prop="params.smtpPass" label="邮箱密码/授权码">
								<el-input v-model="editData.params.smtpPass" type="password" placeholder="邮箱密码或授权码"></el-input>
							</el-form-item>
							<el-form-item prop="params.from" label="发件人邮箱">
								<el-input v-model="editData.params.from" placeholder="your-email@example.com"></el-input>
							</el-form-item>
							<el-form-item prop="params.to" label="收件人邮箱">
								<el-input v-model="editData.params.to" placeholder="recipient@example.com"></el-input>
							</el-form-item>
						</template>
						<el-form-item prop="notSendNull" label="忽略无同步">
							<el-switch v-model="editData.params.notSendNull" :active-value="1" :inactive-value="0">
							</el-switch>
						</el-form-item>
					</el-form>
				</div>
				<span slot="footer" class="dialog-footer">
					<el-button @click="closeShow">取 消</el-button>
					<el-button type="success" :loading="tstLoading" @click="tstCu()">测 试</el-button>
					<el-button type="primary" @click="submit" :loading="editLoading">确 定</el-button>
				</span>
			</el-dialog>
		</div>
	</div>
</template>

<script>
	import {
		getNotifyList,
		delNotify,
		putEnableNotify,
		postAddNotify,
		putEditNotify
	} from '@/api/notify';
	export default {
		name: 'Notify',
		components: {},
		data() {
			return {
				dataList: [],
				loading: false,
				deleteLoading: false,
				editLoading: false,
				tstLoading: false,
				enableLoading: false,
				editData: null,
				editFlag: false,
				editShow: false,
				editRule: [{
						params: {
							url: [{
								type: 'string',
								required: true,
								message: '请输入地址'
							}],
							titleName: [{
								type: 'string',
								required: true,
								message: '请输入标题名'
							}],
							contentName: [{
								type: 'string',
								required: true,
								message: '请输入内容名'
							}]
						}
					}, {
						params: {
							sendKey: [{
								type: 'string',
								required: true,
								message: '请输入sendKey'
							}]
						}
					}, {
						params: {
							url: [{
								type: 'string',
								required: true,
								message: '请输入WebHook地址'
							}]
						}
					}, {
						params: {
							smtpHost: [{
								type: 'string',
								required: true,
								message: '请输入SMTP服务器地址'
							}],
							smtpPort: [{
								type: 'number',
								required: true,
								message: '请输入SMTP端口'
							}],
							smtpUser: [{
								type: 'string',
								required: true,
								message: '请输入SMTP用户名'
							}],
							smtpPassword: [{
								type: 'string',
								required: true,
								message: '请输入SMTP密码/授权码'
							}],
							fromEmail: [{
								type: 'string',
								required: true,
								message: '请输入发件人邮箱'
							}],
							toEmails: [{
								type: 'string',
								required: true,
								message: '请输入收件人邮箱'
							}]
						}
					}]
			};
		},
		created() {
			this.getData();
		},
		beforeDestroy() {},
		methods: {
			getData() {
				this.loading = true;
				getNotifyList().then(res => {
					this.loading = false;
					this.dataList = res.data;
				}).catch(err => {
					this.loading = false;
				})
			},
			// 跳转到消息记录页面
			goToLog() {
				this.$router.push('/notify/log');
			},
			addShow() {
				this.editFlag = false;
				this.editData = {
					enable: 1,
					method: 1,
					params: {
						sendKey: '',
						notSendNull: false
					}
				}
				this.editShow = true;
			},
			editShowDialog(row) {
				let editData = JSON.parse(JSON.stringify(row));
				editData.params = JSON.parse(editData.params);
				if (!editData.params.hasOwnProperty('notSendNull')) {
					editData.params['notSendNull'] = false;
				}
				this.editData = editData;
				this.editFlag = true;
				this.editShow = true;
			},
			methodChange(val) {
						if (val === 0) {
							this.editData.params = {
								url: '',
								method: 'POST',
								contentType: 'application/json',
								needContent: true,
								titleName: 'title',
								contentName: 'content',
								notSendNull: false
							}
						} else if (val === 1) {
							this.editData.params = {
								sendKey: '',
								notSendNull: false
							}
						} else if (val === 2) {
							this.editData.params = {
								url: '',
								notSendNull: false
							}
						} else if (val === 3) {
							this.editData.params = {
								smtpHost: '',
								smtpPort: 465,
								smtpUser: '',
								smtpPassword: '',
								fromEmail: '',
								toEmails: '',
								ssl: 1,
								tls: 0,
								notSendNull: false
							}
						}
						this.$nextTick(() => {
							this.$refs.addRule.clearValidate();
						})
					},
			closeShow() {
				this.editShow = false;
			},
			enableNotify(notifyId, enable) {
				this.enableLoading = true;
				putEnableNotify(notifyId, enable).then(res => {
					this.enableLoading = false;
					this.$message({
						message: res.msg,
						type: 'success'
					});
					this.getData();
				}).catch(err => {
					this.enableLoading = false;
				})
			},
			submit() {
				this.$refs.addRule.validate((valid) => {
					if (valid) {
						let dt = JSON.parse(JSON.stringify(this.editData));
						dt.params = JSON.stringify(dt.params);
						this.editLoading = true;
						if (this.editFlag) {
							putEditNotify(dt).then(res => {
								this.editLoading = false;
								this.$message({
									message: res.msg,
									type: 'success'
								});
								this.closeShow();
								this.getData();
							}).catch(err => {
								this.editLoading = false;
							})
						} else {
							postAddNotify(dt).then(res => {
								this.editLoading = false;
								this.$message({
									message: res.msg,
									type: 'success'
								});
								this.closeShow();
								this.getData();
							}).catch(err => {
								this.editLoading = false;
							})
						}
					}
				})
			},
			tstCu(item = null) {
				if (item == null) {
					this.$refs.addRule.validate((valid) => {
						if (valid) {
							this.tstCuTrueDo(this.editData);
						}
					})
				} else {
					this.tstCuTrueDo(item);
				}
			},
			tstCuTrueDo(item) {
				this.tstLoading = true;
				let it = JSON.parse(JSON.stringify(item));
				if (typeof it.params === 'object' && it.params !== null) {
					it.params = JSON.stringify(it.params);
				}
				delete it.enable;
				postAddNotify(it).then(res => {
					this.tstLoading = false;
					this.$message({
						message: '测试消息已发送，请检查是否正确收到通知',
						type: 'success'
					});
				}).catch(err => {
					this.tstLoading = false;
				})
			},
			delCu(id) {
				this.$confirm("操作不可逆，将永久删除该通知配置，仍要删除吗？", '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					this.deleteLoading = true;
					delNotify(id).then(res => {
						this.deleteLoading = false;
						this.$message({
							message: res.msg,
							type: 'success'
						});
						this.getData();
					}).catch(err => {
						this.deleteLoading = false;
					})
				});
			}
		}
	}
</script>

<style lang="scss">
	.tip-box {
		margin: 0 0 20px 100px;
		color: var(--text-secondary);

		a {
			color: var(--color-primary);
		}

		a:hover {
			color: #66b1ff;
		}
	}

	.full-width {
		width: 100%;
	}

	.card-item-logo {
		width: 60px;
		height: 60px;
	}

	.card-item-info {
		margin-left: 12px;
	}

	.notify {
		box-sizing: border-box;
		width: 100%;
		height: 100%;
		padding: 16px;

		.header-box {
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 16px;
			
			h2 {
				margin: 0;
				color: var(--text-primary);
			}
		}

		.loading-box {
			box-sizing: border-box;
			width: 100%;
			height: 100%;
		}

		.card-box {
			box-sizing: border-box;
			padding: 8px;
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(380px, 2fr));
			width: 100%;

			.card-item {
				background-color: var(--bg-quaternary);
				border-radius: 5px;
				border: 1px solid;
				border-color: transparent;
				height: 110px;
				margin: 8px;
				padding: 6px;
				color: var(--text-primary);

				.card-item-top {
					display: flex;
					align-items: center;
					justify-content: center;

					.card-item-user {
						font-size: 18px;
						display: flex;
					}

					.card-item-enable {
						margin-top: 6px;
						font-weight: bold;
					}

					.enable-enable {
						color: #67c23a;
					}

					.enable-disable {
						color: #f56c6c;
					}
				}

				.card-item-bottom {
					display: flex;
					align-items: center;
					justify-content: center;
					margin-top: 12px;
				}
			}

			.card-add {
				font-size: 32px;
				cursor: pointer;
				display: flex;
				justify-content: center;
				align-items: center;
				color: var(--text-primary);
				
				.highlight-text {
					color: var(--color-primary);
				}
			}

			.card-item:hover {
				border-color: #409eff;
				background-color: var(--card-hover);
			}

			.card-add:hover {
				font-size: 32px;
				color: #409eff;
				font-weight: bold;
			}
		}
	}
</style>
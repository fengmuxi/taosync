<template>
	<div class="login" :class="vuex_theme">
		<div class="loginArea" :class="vuex_theme">
			<div class="logo">桃桃的自动同步工具</div>
			<div class="title">密码登录</div>
			<el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="0">
				<el-form-item prop="userName">
					<el-input class="input" placeholder="请输入用户名" prefix-icon="el-icon-user"
						v-model="loginForm.userName"></el-input>
				</el-form-item>
				<el-form-item prop="passwd">
					<el-input placeholder="请输入密码" prefix-icon="el-icon-lock" v-model="loginForm.passwd" show-password
						@keyup.enter.native="login"></el-input>
				</el-form-item>
			</el-form>
			<div class="foget" @click="fogetPwd">忘记密码？</div>
			<el-button class="login-button" size="medium" type="primary" :loading="loading"
				@click="login">登录</el-button>
		</div>
		<!-- 主题切换按钮 -->
		<div class="theme-switch" @click="toggleTheme">
			<i :class="vuex_theme === 'dark' ? 'el-icon-moon' : 'el-icon-sunny'"></i>
			<span>{{ vuex_theme === 'dark' ? '浅色' : '深色' }}</span>
		</div>
		<el-dialog :close-on-click-modal="false" :visible.sync="showPwd" :append-to-body="true" title="重置密码"
			width="90%" max-width="560px" :before-close="closePwd">
			<div>
				<el-form :model="pwdForm" :rules="pwdRules" ref="resetForm" label-width="80px">
					<el-form-item prop="userName" label="用户名">
						<el-input class="input" placeholder="请输入用户名" v-model="pwdForm.userName"></el-input>
					</el-form-item><el-form-item prop="key" label="加密秘钥">
						<el-input class="input" placeholder="在[程序同级]或[docker挂载]目录[data/secret.key]文件中复制全部"
							v-model="pwdForm.key"></el-input>
					</el-form-item>
					<el-form-item prop="passwd" label="新密码">
						<el-input placeholder="请输入新密码" v-model="pwdForm.passwd" show-password></el-input>
					</el-form-item>
					<el-form-item prop="passwd2" label="确认密码">
						<el-input placeholder="请确认新密码" v-model="pwdForm.passwd2" show-password></el-input>
					</el-form-item>
				</el-form>
			</div>
			<span slot="footer" class="dialog-footer">
				<el-button @click="closePwd">取 消</el-button>
				<el-button type="primary" @click="fogetSubmit" :loading="loading">确 定</el-button>
			</span>
		</el-dialog>
	</div>
</template>

<script>
	import Cookies from 'js-cookie';
	import {
		login,
		resetPwd
	} from "@/api/user";
	export default {
		name: 'Login',
		data() {
			var validatePass2 = (rule, value, callback) => {
				if (value == '' || value == null) {
					callback(new Error('请再次输入新密码'));
				} else if (value !== this.pwdForm.passwd) {
					callback(new Error('两次输入密码不一致!'));
				} else {
					callback();
				}
			};
			return {
				loginForm: {
					userName: null,
					passwd: null
				},
				loading: false,
				rules: {
					userName: [{
						required: true,
						message: '请输入用户名',
						trigger: 'blur'
					}],
					passwd: [{
						required: true,
						message: '请输入密码',
						trigger: 'blur'
					}]
				},
				pwdRules: {
					userName: [{
						required: true,
						message: '请输入用户名',
						trigger: 'blur'
					}],
					key: [{
						required: true,
						message: '请输入key',
						trigger: 'blur'
					}],
					passwd: [{
						required: true,
						message: '请输入新密码',
						trigger: 'blur'
					}],
					passwd2: [{
						validator: validatePass2,
						trigger: 'blur'
					}]
				},
				showPwd: false,
				pwdForm: {
					userName: null,
					key: null,
					passwd: null,
					passwd2: null
				}
			};
		},
		created() {
			// 初始化主题
			document.documentElement.className = this.vuex_theme;
		},
		methods: {
			login() {
				this.$refs.loginForm.validate((valid) => {
					if (valid) {
						Cookies.remove(this.vuex_cookieName);
						this.loading = true;
						login(this.loginForm).then(res => {
							this.$setVuex('vuex_userInfo', res.data);
							this.$router.replace('/home');
							this.loading = false;
						}).catch(err => {
							this.loading = false;

						})
					} else {
						return false;
					}
				});
			},
			fogetPwd() {
				this.showPwd = true;
			},
			closePwd() {
				this.showPwd = false;
				this.pwdForm = {
					userName: null,
					key: null,
					passwd: null,
					passwd2: null
				}
			},
			fogetSubmit() {
				this.$refs.resetForm.validate((valid) => {
					if (valid) {
						this.loading = true;
						resetPwd(this.pwdForm).then(res => {
							this.closePwd();
							this.$message({
								message: '密码重置成功，请使用新密码登录',
								type: 'success'
							});
							this.loading = false;
						}).catch(err => {
							this.loading = false;
						})
					} else {
						return false;
					}
				});
			},
			toggleTheme() {
				// 切换主题模式
				const newTheme = this.vuex_theme === 'dark' ? 'light' : 'dark';
				this.$setVuex('vuex_theme', newTheme);
				// 标记用户已手动设置主题
				this.$setVuex('vuex_theme_manually_set', true);
				document.documentElement.className = newTheme;
			}
		}
	}
</script>
<style lang="scss" scoped>
	.login {
		display: flex;
		align-items: center;
		justify-content: center;
		position: fixed;
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		background: url(~@/assets/img/login-bg.jpg) no-repeat center;
		background-size: cover;
		// 在移动端调整背景图片大小
		@media (max-width: 768px) {
			background-size: auto 100%;
		}

		// 浅色主题背景遮罩
		&.light {
			&::before {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				bottom: 0;
				background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(245, 247, 250, 0.85) 100%);
				backdrop-filter: blur(10px);
				z-index: 0;
			}

			.loginArea {
				background: rgba(255, 255, 255, 0.98);
				color: var(--text-primary);
				box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
				backdrop-filter: blur(10px);

				:deep(.el-input) {
					.el-input__inner {
						background-color: transparent;
						color: var(--text-primary);
						border: 1px solid var(--border-color);
					}
				}

				.title {
					color: var(--text-primary);
					border-bottom: 1px solid var(--border-color);
				}
			}
		}
		
		// 深色主题 - 黑金配色
		&.dark {
			&::before {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				bottom: 0;
				background: linear-gradient(135deg, rgba(10, 10, 10, 0.98) 0%, rgba(26, 26, 26, 0.95) 100%);
				backdrop-filter: blur(5px);
				z-index: 0;
			}

			.loginArea {
				background: rgba(26, 26, 26, 0.95);
				color: #FFF;
				box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
				backdrop-filter: blur(10px);

				:deep(.el-input) {
					.el-input__inner {
						background-color: transparent;
						color: #FFF;
						border: 1px solid var(--color-primary);
					}
				}

				.title {
					color: var(--color-primary);
					border-bottom: 1px solid var(--border-color);
				}
			}
		}

		.loginArea {
			position: relative;
			z-index: 1;
			width: 90%;
			max-width: 520px;
			box-sizing: border-box;
			padding: 30px;
			border-radius: 8px;
			margin: 0 auto;
			// 在移动端调整内边距和边框圆角
			@media (max-width: 768px) {
				padding: 20px;
				border-radius: 12px;
				width: 95%;
			}

			:deep(.el-input) {
				font-size: 16px;
				// 在移动端调整字体大小
				@media (max-width: 768px) {
					font-size: 14px;
				}

				.el-input__inner {
				height: 50px;
				font-size: 16px;
				// 在移动端调整高度和字体大小
				@media (max-width: 768px) {
					height: 44px;
					font-size: 14px;
				}
				}

				.el-input__inner:focus {
				border: 1px solid #409eff;
				}
			}

			:deep(.el-form-item.is-error .el-input__inner) {
				border: 1px solid #F56C6C;
			}

			:deep(.el-input--prefix .el-input__inner) {
				padding-left: 40px;
				// 在移动端调整内边距
				@media (max-width: 768px) {
					padding-left: 35px;
				}
			}

			:deep(.el-form-item) {
				margin-bottom: 20px;
				// 在移动端调整间距
				@media (max-width: 768px) {
					margin-bottom: 15px;
				}

				.el-form-item__error {
				font-size: 14px;
				// 在移动端调整字体大小
				@media (max-width: 768px) {
					font-size: 12px;
				}
				}
			}

			:deep(.el-button--primary) {
				font-size: 18px;
				padding: 15px 20px;
				// 在移动端调整字体大小和内边距
				@media (max-width: 768px) {
					font-size: 16px;
					padding: 12px 20px;
				}
			}

			.logo {
				background-image: url('/logo-200-64.png');
				background-position: center 0;
				background-repeat: no-repeat;
				width: 100%;
				max-width: 600px;
				padding-top: 80px;
				text-align: center;
				letter-spacing: 6px;
				font-size: 20px;
				// 在移动端调整字体大小
				@media (max-width: 768px) {
					font-size: 16px;
					background-size: contain;
					padding-top: 60px;
				}
			}

			.title {
				margin-top: 40px;
				font-size: 24px;
				font-weight: 500;
				line-height: 28px;
				text-align: center;
				padding-bottom: 13px;
				margin-bottom: 30px;
				position: relative;
				// 在移动端调整间距和字体大小
				@media (max-width: 768px) {
					margin-top: 30px;
					font-size: 20px;
					margin-bottom: 20px;
				}

				&::after {
				content: "";
				display: block;
				width: 53px;
				height: 6px;
				background: url(~@/assets/img/login-line-rectangle.png);
				background-size: contain;
				background-repeat: no-repeat;
				margin: 0 auto;
				position: absolute;
				bottom: 0;
				left: 50%;
				transform: translateX(-50%);
				}
			}

			.login-button {
				width: 100%;
				margin: 20px 0 20px 0;
				// 在移动端调整间距
				@media (max-width: 768px) {
					margin: 15px 0 15px 0;
				}
			}

			.foget {
				text-align: right;
				cursor: pointer;
				color: #409eff;
				font-size: 14px;
				// 在移动端调整字体大小
				@media (max-width: 768px) {
					font-size: 12px;
				}
			}
		}

		// 主题切换按钮样式
		.theme-switch {
			position: absolute;
			top: 20px;
			right: 20px;
			display: flex;
			align-items: center;
			gap: 8px;
			padding: 8px 16px;
			background-color: rgba(0, 0, 0, 0.2);
			border-radius: 20px;
			cursor: pointer;
			color: #fff;
			font-size: 14px;
			transition: all 0.3s ease;
			z-index: 1000;

			&:hover {
				background-color: rgba(0, 0, 0, 0.3);
			}

			&.light {
				background-color: rgba(255, 255, 255, 0.8);
				color: var(--text-primary);

				&:hover {
					background-color: rgba(255, 255, 255, 0.9);
				}
			}

			i {
				font-size: 18px;
			}
		}
	}
</style>
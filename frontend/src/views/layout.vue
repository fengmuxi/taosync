<template>
	<div class="layout">
		<!-- 侧边栏遮罩层 -->
		<div v-if="!isMobileCollapse && isMobile" class="sidebar-mask" @click="toggleMobileSidebar"></div>
		
		<!-- 左侧边栏 -->
		<div class="lay-left" :class="{ 'mobile-show': !isMobileCollapse && isMobile }">
			<div class="left-top-logo">
				<div :class="'left-top-logo-in ' + (isCollapse ? 'isCollapse' : '')" @click="toIndex"></div>
			</div>
			<el-menu :default-active="vuex_letfIndex" :router="true" :collapse="isCollapse && !isMobile" class="lay-left-menu">
				<el-menu-item :index="item.index" v-for="item in menuList" :key="item.index">
					<i :class="`el-icon-${item.icon}`"></i>
					<span slot="title">{{item.title}}</span>
				</el-menu-item>
			</el-menu>
		</div>
		
		<!-- 右侧内容区域 -->
		<div class="lay-right">
			<!-- 顶部导航栏 -->
			<div class="lay-right-top">
				<div class="top-left">
					<!-- 移动端侧边栏切换按钮 -->
					<div class="top-icon can-click" @click="isMobile ? toggleMobileSidebar : (isCollapse = !isCollapse)">
						<i :class="(isMobile && isMobileCollapse) || (!isMobile && isCollapse) ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
					</div>
				</div>
				<div class="top-right">
					<div class="btn-item can-click" @click="toggleTheme">
						<div class="top-icon">
							<i :class="vuex_theme === 'dark' ? 'el-icon-moon' : 'el-icon-sunny'"></i>
						</div>
						<span class="hide-mobile">{{ vuex_theme === 'dark' ? '浅色' : '深色' }}</span>
					</div>
					<div class="btn-item can-click" @click="logout()">
						<div class="top-icon">
							<i class="el-icon-switch-button"></i>
						</div>
						<span class="hide-mobile">登出</span>
					</div>
				</div>
			</div>
			
			<!-- 主内容区域 -->
			<div class="lay-right-bottom" v-loading="vuex_loading" :class="{ 'mobile-full': isMobile && isMobileCollapse }">
				<router-view />
			</div>
			
			<!-- 移动端底部导航栏 -->
			<div class="mobile-bottom-nav" v-if="isMobile">
				<div 
					v-for="item in menuList" 
					:key="item.index"
					class="nav-item"
					:class="{ 'active': vuex_letfIndex === item.index }"
					@click="navigateTo(item.index)"
				>
					<i :class="`el-icon-${item.icon}`"></i>
					<span>{{ item.title }}</span>
				</div>
			</div>
		</div>

	</div>
</template>
<script>
	import {
		logout
	} from "@/api/user";
	export default {
		data() {
			return {
				isCollapse: false,
				isMobile: false,
				isMobileCollapse: true,
				menuList: [{
						index: '/home',
						title: '作业管理',
						icon: 'data-analysis'
					},{
						index: '/engine',
						title: '引擎管理',
						icon: 'receiving'
					},{
						index: '/notify',
						title: '通知配置',
						icon: 'bell'
					},{
						index: '/feiniu',
						title: '飞牛配置',
						icon: 'cpu'
					},{
						index: '/setting',
						title: '系统设置',
						icon: 'setting'
					}]
			};
		},
		created() {
			this.init();
			// 监听窗口大小变化
			window.addEventListener('resize', this.handleResize);
			// 初始化检测设备类型
			this.handleResize();
		},
		beforeDestroy() {
			// 移除事件监听
			window.removeEventListener('resize', this.handleResize);
		},
		watch: {},
		methods: {
			init() {},
			// 检测窗口大小，判断是否为移动设备
			handleResize() {
				this.isMobile = window.innerWidth <= 768;
				// 在移动设备上默认隐藏侧边栏
				if (this.isMobile) {
					this.isMobileCollapse = true;
				}
			},
			// 切换移动端侧边栏显示/隐藏
			toggleMobileSidebar() {
				this.isMobileCollapse = !this.isMobileCollapse;
			},
			logout() {
				logout().then(res => {
					this.$router.push('/login');
					this.$setVuex('vuex_userInfo', null);
				})
			},
			toIndex() {
				this.$router.push('/');
			},
			toggleTheme() {
				// 切换主题模式
				const newTheme = this.vuex_theme === 'dark' ? 'light' : 'dark';
				this.$setVuex('vuex_theme', newTheme);
				// 标记用户已手动设置主题
				this.$setVuex('vuex_theme_manually_set', true);
			},
			// 导航到指定路由
			navigateTo(path) {
				this.$router.push(path);
			}
		}
	}
</script>
<style lang="scss" scoped>
	.layout {
		position: fixed;
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		background-color: var(--bg-primary);
		color: var(--text-primary);

		// 侧边栏遮罩层
		.sidebar-mask {
			position: fixed;
			top: 0;
			left: 0;
			right: 0;
			bottom: 0;
			background-color: rgba(0, 0, 0, 0.5);
			z-index: 998;
			transition: all 0.3s ease;
			// 在PC端隐藏遮罩
			@media (min-width: 769px) {
				display: none;
			}
		}

		// 左侧边栏
		.lay-left {
			background-color: var(--bg-secondary);
			z-index: 999;
			transition: all 0.3s ease;
			// 在移动端默认隐藏
			@media (max-width: 768px) {
				position: fixed;
				left: -140px;
				top: 0;
				height: 100%;
				bottom: 0;
			}

			// 移动端侧边栏显示状态
			&.mobile-show {
				@media (max-width: 768px) {
					left: 0;
				}
			}

			.left-top-logo {
				height: 67px;
				display: flex;
				align-items: center;
				justify-content: center;

				.left-top-logo-in {
					width: 140px;
					height: 44.8px;
					cursor: pointer;
					background-image: url('/logo-200-64.png');
					background-size: 140px 44.8px;
					transition: all .3s ease-in-out;
					background-repeat: no-repeat;
					background-position: 0 0;
				}

				.isCollapse {
					width: 44.8px;
				}
			}

			.lay-left-menu {
				height: 100%;
			}

			.lay-left-menu:not(.el-menu--collapse) {
				width: 140px;
			}
		}

		// 右侧内容区域
		.lay-right {
			width: 100%;
			height: 100%;
			transition: all 0.3s ease;

			// 顶部导航栏
			.lay-right-top {
				height: 56px;
				display: flex;
				justify-content: space-between;
				align-items: center;
				border-bottom: 1px solid var(--border-color);
				font-size: 16px;

				.top-icon {
					height: 56px;
					width: 56px;
					display: flex;
					align-items: center;
					justify-content: center;
					font-size: 24px;
					// 确保触控区域不小于44x44像素
					min-height: 44px;
					min-width: 44px;
				}

				.can-click {
					cursor: pointer;
					// 确保触控区域不小于44x44像素
					min-height: 44px;
					min-width: 44px;
					display: flex;
					align-items: center;
					justify-content: center;
				}

				.can-click:hover {
					background-color: var(--bg-quaternary);
				}

				.top-left {
					display: flex;
					align-items: center;
				}

				.top-right {
					display: flex;
					align-items: center;

					.btn-item {
						display: flex;
						align-items: center;
						padding-right: 20px;
						cursor: pointer;
						// 确保触控区域不小于44x44像素
						min-height: 44px;
						min-width: 44px;

						// 在移动端隐藏文字，只显示图标
						@media (max-width: 768px) {
							span {
								display: none;
							}
							padding-right: 16px;
							// 移动端确保足够的触控区域
							padding-left: 16px;
						}
					}
				}
			}

			// 主内容区域
			.lay-right-bottom {
				height: calc(100% - 57px);
				overflow-y: auto;
				transition: width .3s ease-in-out;

				// 在移动端内容区域宽度自适应
				&.mobile-full {
					@media (max-width: 768px) {
						width: 100% !important;
					}
				}
			}
		}

		// 响应式调整
		@media (max-width: 768px) {
			// 确保lay-right-bottom在移动端宽度正确
			.lay-right-bottom {
				width: 100% !important;
				// 调整高度计算，考虑顶部导航栏(48px)和底部导航栏(64px)高度
				height: calc(100% - 48px - 64px) !important;
				// 添加底部内边距，确保内容不被底部导航栏遮挡
				padding-bottom: 64px !important;
			}
			
			// 调整按钮大小，确保触摸友好
			.top-icon {
				width: 44px !important;
				height: 44px !important;
				font-size: 20px !important;
				// 确保触控区域不小于44x44像素
				min-height: 44px !important;
				min-width: 44px !important;
			}
			
			// 调整顶部导航栏高度
			.lay-right-top {
				height: 48px !important;
			}
		}

		// 平板及以上设备样式
		@media (min-width: 769px) {
			.lay-right-bottom {
				width: calc(100vw - 140px) !important;
			}
			
			// 折叠状态下的宽度
			.lay-left-menu.el-menu--collapse + .lay-right .lay-right-bottom {
				width: calc(100vw - 64px) !important;
			}
		}
	}

	// 隐藏移动端不需要显示的元素
	.hide-mobile {
		@media (max-width: 768px) {
			display: none;
		}
	}

	// 移动端底部导航栏
.mobile-bottom-nav {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 64px;
	background-color: var(--bg-secondary);
	border-top: 1px solid var(--border-color);
	display: flex;
	align-items: center;
	justify-content: space-around;
	z-index: 999;
	box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
	
	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 8px 12px;
		min-width: 70px;
		min-height: 44px;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s ease;
		user-select: none;
		
		i {
			font-size: 22px;
			margin-bottom: 4px;
			transition: all 0.2s ease;
		}
		
		span {
			font-size: 12px;
			transition: all 0.2s ease;
		}
		
		// 激活状态样式
		&.active {
			color: var(--color-primary);
			font-weight: 500;
			
			i {
				transform: scale(1.1);
			}
			
			span {
				font-weight: 600;
			}
		}
		
		//  hover状态样式
		&:hover {
			color: var(--text-primary);
			i {
				transform: translateY(-2px);
			}
		}
	}
	
	// 在桌面端隐藏底部导航栏
	@media (min-width: 769px) {
		display: none;
	}
	
	// 在小屏手机上调整字体大小和图标大小
	@media (max-width: 374px) {
		.nav-item {
			min-width: 60px;
			
			i {
				font-size: 20px;
			}
			
			span {
				font-size: 11px;
			}
		}
	}
}
</style>

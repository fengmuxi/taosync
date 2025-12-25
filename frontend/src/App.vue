<template>
	<div id="app" class="app-all-main" :class="vuex_theme">
		<div>
			<router-view />
		</div>
	</div>
</template>
<script>
	export default {
		name: "App",
		data() {
			return {
				timer: null
			};
		},
		watch: {
			$route(to, from) {
				this.$setVuex('vuex_letfIndex', to.meta ? (to.meta.letfIndex || null) : null);
			},
			vuex_theme(newVal) {
				// 主题变化时，更新根元素的类名
				document.documentElement.className = newVal;
			}
		},
		created() {
			// 初始化主题
			// 如果用户没有手动设置过主题，则使用系统偏好设置
			if (!this.vuex_theme_manually_set) {
				const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
				const systemTheme = prefersDarkScheme ? 'dark' : 'light';
				this.$setVuex('vuex_theme', systemTheme);
			} else {
				document.documentElement.className = this.vuex_theme;
			}
			
			// 监听系统主题变化
			window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
				// 只有在用户没有手动设置过主题时才跟随系统变化
				if (!this.vuex_theme_manually_set) {
					const newTheme = e.matches ? 'dark' : 'light';
					this.$setVuex('vuex_theme', newTheme);
				}
			});
		},
		beforeDestroy() {},
		methods: {}
	};
</script>
<style lang="scss">
	body {
		margin: 0;
		padding: 0;
		font-size: 16px;
	}

	/* 全局过渡效果，确保主题切换时有平滑的过渡 */
	* {
		transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
	}

	/* 排除某些元素不需要过渡效果 */
	img, video, canvas, iframe {
		transition: none !important;
	}

	::-webkit-scrollbar {
		width: 5px;
		height: 5px;
	}

	::-webkit-scrollbar-thumb {
		background-color: #3c3f4d;
		transition: background-color 0.3s ease;
	}

	::-webkit-scrollbar-track {
		-webkit-box-shadow: transparent;
		background: transparent;
	}

	.app-all-main {}
</style>
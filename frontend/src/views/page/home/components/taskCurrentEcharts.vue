<template>
	<div class="taskCurrentEcharts" ref="taskCurrentEcharts"></div>
</template>

<script>
	import * as echarts from "echarts";
	import {
		parseSize
	} from "@/utils/utils";
	export default {
		name: 'DlEcharts',
		props: {
			taskCurrent: {
				type: Object,
				default: {}
			}
		},
		data() {
			return {
				chart: null,
				observer: null,
				currentTheme: this.$store.state.vuex_theme // 当前主题
			};
		},
		watch: {
			taskCurrent(newVal, oldVal) {
				if (JSON.stringify(oldVal) != JSON.stringify(newVal)) {
					this.$nextTick(() => {
						this.initChart();
					});
				}
			},
			'$store.state.vuex_theme'(newTheme) {
				// 主题变化时重新初始化图表
				this.currentTheme = newTheme;
				this.destroy();
				this.$nextTick(() => {
					this.initChart();
				});
			}
		},
		created() {
			this.$nextTick(() => {
				this.initChart();
				this.initResizeObserver();
			});
		},
		beforeDestroy() {
			this.destroy();
		},
		methods: {
			destroy() {
				if (this.chart) {
					this.chart.dispose();
					this.chart = null;
				}
				if (this.observer) {
					this.observer.disconnect();
					this.observer = null;
				}
			},
			initResizeObserver() {
				const element = this.$refs.taskCurrentEcharts;
				this.observer = new ResizeObserver(entries => {
					for (const entry of entries) {
						this.resize();
					}
				});
				this.observer.observe(element);
			},
			initChart() {
				// 原始数据
				const rawData = {
					num: this.taskCurrent.num,
					size: this.taskCurrent.size
				};
				const keyVal = {
					wait: '等待中',
					running: '进行中',
					success: '成功',
					fail: '失败',
					other: '其他'
				};
				let d0 = [];
				Object.entries(keyVal).forEach(([key, val]) => {
					d0.push({
						name: val,
						value: this.taskCurrent.num[key]
					})
				})
				let d1 = [];
				Object.entries(keyVal).forEach(([key, val]) => {
					d1.push({
						name: val,
						value: this.taskCurrent.size[key]
					})
				})
				
				// 根据主题设置颜色
				const isDark = this.currentTheme === 'dark';
				const colors = isDark ? 
					['rgb(79, 89, 104)', 'rgb(64, 158, 255)', 'rgb(103, 194, 58)', 'rgb(245, 108, 108)', 'rgb(230, 162, 60)'] :
					['rgb(120, 144, 156)', 'rgb(41, 121, 255)', 'rgb(76, 175, 80)', 'rgb(244, 67, 54)', 'rgb(255, 152, 0)'];
				
				// 设置图例文字颜色
				const legendTextColor = isDark ? '#c0c4cc' : '#606266';
				
				// ECharts 配置
				const option = {
					color: colors,
					tooltip: {
						trigger: 'item',
						backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
						textStyle: {
							color: isDark ? '#c0c4cc' : '#606266'
						}
					},
					legend: {
						top: '5%',
						left: 'center',
						textStyle: {
							color: legendTextColor
						}
					},
					series: [{
							name: '文件及目录数量',
							type: 'pie',
							radius: ['75%', '90%'],
							center: ['50%', '86%'],
							startAngle: 180,
							endAngle: 360,
							data: d0,
							label: {
								color: legendTextColor
							},
							labelLine: {
								lineStyle: {
									color: isDark ? 'rgba(192, 196, 204, 0.3)' : 'rgba(96, 98, 102, 0.3)'
								}
							}
						}, {
							name: '文件大小',
							type: 'pie',
							radius: [0, '65%'],
							center: ['50%', '86%'],
							startAngle: 180,
							endAngle: 360,
							label: {
								position: 'inside',
								color: '#fff'
							},
							tooltip: {
								valueFormatter: (value) => parseSize(value),
								backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
								textStyle: {
									color: isDark ? '#c0c4cc' : '#606266'
								}
							},
							data: d1
						}]
				};
				if (!this.chart) {
					// 根据当前主题初始化图表
					this.chart = echarts.init(this.$refs.taskCurrentEcharts, this.currentTheme);
				}
				this.chart.setOption(option);
			},
			resize() {
				if (this.chart) {
					this.chart.resize();
				}
			}
		}
	}
</script>

<style lang="scss" scoped>
	.taskCurrentEcharts {}
</style>
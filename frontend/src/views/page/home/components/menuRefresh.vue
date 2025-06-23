<template>
	<div class="menuRefresh">
		<el-select v-show="needShow > 1" v-model="interval" placeholder="筛选操作类型" @change="refreshTime" style="width: 140px;margin-right: 10px">
      <el-option v-for="(item,index) in timeList" :label="item.title" :value="item.value"></el-option>
    </el-select>
		<div class="refreshLabel" v-show="needShow > 2">{{refreshText}}</div>
		<el-switch v-model="refreshStatus" v-show="needShow > 2" @change="refreshChange"></el-switch>
		<i :class="`${loading ? 'el-icon-loading' : 'el-icon-refresh-right'} icon-btn`" @click="refreshData" v-show="needShow > 0"></i>
	</div>
</template>

<script>
	export default {
		name: 'MenuRefresh',
		props: {
			loading: {
				type: Boolean,
				default: false
			},
			autoRefresh: {
				type: Boolean,
				default: true
			},
      freshInterval: {
        type: Number,
        default: 3 * 1000
      },
			needShow: {
				type: Number,
				default: 3 // 0-不显示，1-只显示刷新按钮，2-显示刷新间隔 3-显示全部
			},
			refreshText: {
				type: String,
				default: '自动刷新'
			}
		},
		data() {
			return {
				refreshStatus: true,
				timer: null,
        interval: 3000,
        timeList: [
          {
            title: '1秒',
            value: 1 * 1000
          },
          {
            title: '3秒',
            value: 3 * 1000
          },
          {
            title: '5秒',
            value: 5 * 1000
          },
          {
            title: '10秒',
            value: 10 * 1000
          },
          {
            title: '15秒',
            value: 15 * 1000
          },
        ]
			};
		},
    created() {
			this.refreshStatus = this.autoRefresh;
			this.interval = this.freshInterval;
			if (this.refreshStatus) {
				this.startRefresh();
			} else {
				this.$emit('getData');
			}
		},
		beforeDestroy() {
			this.destroy();
		},
		methods: {
      refreshTime(){
        this.destroy();
        this.startRefresh();
      },
			refreshChange(val) {
				this.refreshStatus = val;
				if (val) {
					this.startRefresh();
				} else {
					this.destroy();
				}
			},
			refreshData() {
				if (!this.loading) {
					this.$emit('getData');
				}
			},
			startRefresh() {
				this.destroy();
				this.$emit('getData');
				this.timer = setInterval(() => {
					this.$emit('getData');
				}, this.interval);
			},
			destroy() {
				if (this.timer) {
					clearInterval(this.timer);
				}
			}
		}
	}
</script>

<style lang="scss" scoped>
	.menuRefresh {
		display: flex;
		align-items: center;

		.refreshLabel {
			font-size: 18px;
			margin-right: 8px;
		}

		.icon-btn {
			font-size: 28px;
			margin-left: 24px;
		}

		.el-icon-refresh-right {
			cursor: pointer;
			color: #1890ff;
		}

		.el-icon-loading {
			cursor: not-allowed;
		}
	}
</style>

<template>
	<div class="home">
		<div class="top-box">
			<div class="top-box-left">
				<el-button type="success" icon="el-icon-plus" @click="addShow" size="small">新建作业</el-button>
				<el-button @click="runAllJob" size="small" v-if="jobData.dataList.length > 1" icon="el-icon-caret-right"
					:loading="btnLoading" type="primary">执行全部</el-button>
			</div>
			<div class="top-box-title">作业管理</div>
			<menuRefresh :autoRefresh="false" :freshInterval="5000" :loading="loading" @getData="getJobList">
			</menuRefresh>
		</div>
		<el-table :data="jobData.dataList" class="table-data" height="calc(100% - 117px)" v-loading="loading">
			<el-table-column type="expand">
				<template slot-scope="props">
					<div class="job-detail">
						<!-- 基本信息卡片 -->
						<div class="info-card">
							<div class="info-header">
								<h3 class="info-title">{{ props.row.remark || '未命名作业' }}</h3>
								<span class="job-status" :class="props.row.enable ? 'enabled' : 'disabled'">
									{{ props.row.enable ? '已启用' : '已禁用' }}
								</span>
							</div>
							<div class="info-content">
								<div class="info-grid">
									<div class="info-item">
										<span class="info-label">创建时间</span>
										<span class="info-value">{{ props.row.createTime | timeStampFilter }}</span>
									</div>
									<div class="info-item">
										<span class="info-label">同步方式</span>
										<span class="info-value">
											<span class="method-tag" :class="`method-${props.row.method}`">
												{{ props.row.method == 0 ? '仅新增' : (props.row.method == 1 ? '全同步' : (props.row.method == 2 ? '移动模式' : 'STRM模式'))}}
											</span>
										</span>
									</div>
									<div class="info-item">
										<span class="info-label">调用方式</span>
										<span class="info-value">
											<span class="cron-tag" :class="`cron-${props.row.isCron}`">
												{{ props.row.isCron == 0 ? '间隔' : (props.row.isCron == 1 ? 'Cron' : '仅手动') }}
											</span>
										</span>
									</div>
									<div class="info-item" v-if="props.row.isCron == 0">
										<span class="info-label">同步间隔</span>
										<span class="info-value">{{ props.row.interval }} 分钟</span>
									</div>
								</div>
							</div>
						</div>

						<!-- 配置卡片 -->
						<div class="config-section">
							<h4 class="section-title">
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="section-icon"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
								配置详情
							</h4>

							<!-- 扫描配置 -->
							<div class="config-card">
								<div class="config-header">
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="config-icon"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
									<span class="config-title">扫描配置</span>
								</div>
								<div class="config-content">
									<div class="config-grid">
										<div class="config-item">
											<span class="config-label">目标目录扫描</span>
											<span class="config-value">
												{{ props.row.useCacheT == 0 ? '不用缓存' : '使用缓存' }}，间隔 {{ props.row.scanIntervalT }} 秒
											</span>
										</div>
										<div class="config-item">
											<span class="config-label">源目录扫描</span>
											<span class="config-value">
												{{ props.row.useCacheS == 0 ? '不用缓存' : '使用缓存' }}，间隔 {{ props.row.scanIntervalS }} 秒
											</span>
										</div>
									</div>
								</div>
							</div>

							<!-- 匹配规则 -->
							<div class="config-card">
								<div class="config-header">
									<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="config-icon"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
									<span class="config-title">匹配规则</span>
								</div>
								<div class="config-content">
									<div class="config-item full-width">
										<span class="config-label">文件匹配正则</span>
										<span class="config-value code">
											{{ props.row.possess || '未设置' }}
										</span>
									</div>
									<div class="config-item full-width">
										<span class="config-label">排除项规则</span>
										<div class="tag-list">
											<template v-if="props.row.exclude">
												<span v-for="(item, index) in props.row.exclude.split(':')" :key="index" class="tag">
													{{ item }}
												</span>
											</template>
											<span v-else class="empty">未设置</span>
										</div>
									</div>
									<div class="config-item full-width">
										<span class="config-label">路径排除项规则</span>
										<div class="tag-list">
											<template v-if="props.row.ignore_path">
												<span v-for="(item, index) in props.row.ignore_path.split(':')" :key="index" class="tag">
													{{ item }}
												</span>
											</template>
											<span v-else class="empty">未设置</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Cron 配置 -->
							<template v-if="props.row.isCron == 1">
								<div class="config-card">
									<div class="config-header">
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="config-icon"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
										<span class="config-title">Cron 配置</span>
									</div>
									<div class="config-content">
										<div class="config-item full-width">
											<div class="cron-config">
												<span v-for="item in cronList" :key="item.label" class="cron-item" v-if="props.row[item.label]">
													<span class="cron-label">{{ item.label }}:</span>
													<span class="cron-value">{{ props.row[item.label] }}</span>
												</span>
												<span v-if="!props.row.year && !props.row.month && !props.row.day && !props.row.hour && !props.row.minute && !props.row.second" class="empty">
													未配置
												</span>
											</div>
										</div>
									</div>
								</div>
							</template>

							<!-- STRM 配置 -->
							<template v-if="props.row.method == 3">
								<div class="config-card">
									<div class="config-header">
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="config-icon"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
										<span class="config-title">STRM 配置</span>
									</div>
									<div class="config-content">
										<div class="config-grid">
											<div class="config-item">
												<span class="config-label">刮削文件匹配正则</span>
												<span class="config-value code">{{ props.row.strm_nfo || '未设置' }}</span>
											</div>
											<div class="config-item">
												<span class="config-label">STRM文件保存路径</span>
												<span class="config-value">{{ props.row.strm_path || '未设置' }}</span>
											</div>
											<div class="config-item">
												<span class="config-label">STRM文件内容前缀</span>
												<span class="config-value">{{ props.row.strm_url_prefix || '未设置' }}</span>
											</div>
											<div class="config-item">
												<span class="config-label">同步刮削文件到源目录</span>
												<span class="config-value toggle" :class="props.row.strm_src_sync ? 'on' : 'off'">
													{{ props.row.strm_src_sync ? '是' : '否' }}
												</span>
											</div>
											<div class="config-item">
												<span class="config-label">覆盖本地STRM文件</span>
												<span class="config-value toggle" :class="props.row.strm_create_cover ? 'on' : 'off'">
													{{ props.row.strm_create_cover ? '是' : '否' }}
												</span>
											</div>
											<div class="config-item">
												<span class="config-label">覆盖源目录刮削文件</span>
												<span class="config-value toggle" :class="props.row.strm_src_sync_cover ? 'on' : 'off'">
													{{ props.row.strm_src_sync_cover ? '是' : '否' }}
												</span>
											</div>
										</div>

										<!-- 路径映射 -->
										<div class="config-item full-width">
											<span class="config-label">路径映射关系</span>
											<div class="mapping-list">
												<template v-if="props.row.strm_path_mapping">
													<div v-for="(mapping, index) in props.row.strm_path_mapping.split('|')" :key="index" class="mapping-item">
														<div class="mapping-header">
															<span class="mapping-index">{{ index + 1 }}</span>
															<span class="mapping-library">媒体库: {{ getMediaLibraryTitle(mapping.split(':')[1]) }}</span>
														</div>
														<div class="mapping-content">
															<span class="mapping-src">源: {{ mapping.split(':')[0] }}</span>
															<span class="mapping-arrow">→</span>
															<span class="mapping-dst">目标: {{ mapping.split(':')[2] }}</span>
														</div>
													</div>
												</template>
												<span v-else class="empty">未设置</span>
											</div>
										</div>
									</div>
								</div>
							</template>
						</div>

						<!-- 操作按钮 -->
						<div class="action-bar">
							<template v-if="props.row.isCron != 2">
								<el-button type="warning" :loading="btnLoading" size="mini" v-if="props.row.enable"
									@click="disableJobShow(props.row, false)">
									禁用
								</el-button>
								<el-button type="success" :loading="btnLoading" size="mini" v-else
									@click="putJob(props.row, false)">
									启用
								</el-button>
							</template>
							<el-button type="danger" :loading="btnLoading" size="mini"
								@click="disableJobShow(props.row, true)">
								删除
							</el-button>
							<el-button type="primary" :loading="btnLoading" size="mini"
								@click="editJobShow(props.row)">
								编辑
							</el-button>
						</div>
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="remark" label="名称" width="120">
				<template slot-scope="scope">
					{{ scope.row.remark || '--' }}
				</template>
			</el-table-column>
			<el-table-column prop="enable" label="状态" width="80">
				<template slot-scope="scope">
					<div :class="`bg-status bg-${scope.row.enable ? '2' : '7'}`" class="status-bg">
						{{ scope.row.enable ? '启用' : '禁用' }}
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="srcPath" label="来源目录" min-width="50">
				<template slot-scope="scope">
					<div class="pathList">
						<div class="pathBox bg-8">{{ scope.row.srcPath }}</div>
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="dstPath" label="目标目录" min-width="120">
				<template slot-scope="scope">
					<div class="pathList">
						<div class="pathBox bg-1" v-for="item in scope.row.dstPath.split(':')">{{ item }}</div>
					</div>
				</template>
			</el-table-column>
			<el-table-column label="操作" align="center" width="300">
				<template slot-scope="scope">
					<el-button icon="el-icon-caret-right" type="primary" @click="putJob(scope.row)"
						:loading="btnLoading" size="mini">手动执行</el-button>
					<el-button icon="el-icon-document-copy" type="primary" @click="copyJob(scope.row)"
						:loading="btnLoading" size="mini">复制任务</el-button>
					<el-button icon="el-icon-view" type="success" @click="detail(scope.row.id)" :loading="btnLoading"
						size="mini">详情</el-button>
				</template>
			</el-table-column>
		</el-table>
		<div class="page">
			<el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
				:current-page="params.pageNum" :page-size="params.pageSize" :total="jobData.count"
				layout="total, sizes, prev, pager, next, jumper" :page-sizes="[10, 20, 50, 100]">
			</el-pagination>
		</div>
		<el-dialog top="5vh" :close-on-click-modal="false" :visible.sync="editShow" :append-to-body="true"
			:title="`${editData && editData.id != null ? '编辑' : '新增'}作业`" width="900px" :before-close="closeShow">
			<div class="elform-box">
				<el-form :model="editData" :rules="addRule" ref="jobRule" v-if="editShow" label-width="180px">
					<div class="grid-layout">
						<el-form-item prop="enable" label="是否启用">
							<div class="label_width">
								<el-switch v-model="editData.enable" :active-value="1" :inactive-value="0"
									v-if="editData.isCron != 2">
								</el-switch>
								<span v-else>启用</span>
							</div>
						</el-form-item>
						<el-form-item prop="alistId" label="引擎">
			<el-select v-model="editData.alistId" placeholder="请选择引擎" class="label_width"
				no-data-text="暂无引擎,请前往引擎管理创建">
				<el-option v-for="item in alistList" :label="item.url" :value="item.id" :key="item.id">
					<span class="option-left">{{ item.url }}{{ item.remark != null ?
							`[${item.remark}]` : ''}}</span>
					<span class="option-right">{{ item.userName }}</span>
				</el-option>
			</el-select>
		</el-form-item>
						<el-form-item prop="srcPath" label="源目录">
							<div v-if="editData.alistId == null" class="label_width">请先选择引擎</div>
							<div v-else class="label_width">
								{{ editData.srcPath }}
								<el-button type="primary" size="mini"
									:class="{'no-margin': editData.srcPath == ''}"
									@click="selectPath(true)">{{ editData.srcPath == '' ? '选择' : '更换' }}目录</el-button>
							</div>
						</el-form-item>
						<el-form-item prop="dstPath" label="目标目录">
							<div v-if="editData.alistId == null" class="label_width">请先选择引擎</div>
							<div v-else class="label_width">
								<div class="label-list-box">
									<div v-for="(item, index) in editData.dstPath" class="label-list-item">
										<div class="bg-1 label-list-item-left">
											{{ item }}
										</div>
										<el-button type="danger" size="mini" @click="delDstPath(index)">删除</el-button>
									</div>
									<el-button type="primary" size="mini"
										@click="selectPath(false)">{{ editData.dstPath.length
											== 0 ? '选择' : '添加'}}目录</el-button>
								</div>
							</div>
						</el-form-item>
						<el-form-item prop="remark" label="作业名称">
							<div class="label_width">
								<el-input v-model="editData.remark" placeholder="用来标识你的作业，选填"></el-input>
							</div>
						</el-form-item>
						<el-form-item prop="method" label="同步方法">
							<el-select v-model="editData.method" class="label_width">
								<el-option label="仅新增" :value="0">
									<span class="option-left">仅新增</span>
									<span class="option-right">仅新增目标目录没有的文件</span>
								</el-option>
								<el-option label="全同步" :value="1">
									<span class="option-left">全同步</span>
									<span class="option-right">目标目录比源目录多的文件将被删除</span>
								</el-option>
								<el-option label="移动模式" :value="2">
									<span class="option-left">移动模式</span>
									<span class="option-right">同步完成后删除源目录所有文件</span>
								</el-option>
								<el-option label="strm文件生成模式" :value="3">
									<span class="option-left">strm文件生成模式</span>
									<span class="option-right">新增目标目录没有的strm文件并同步刮削信息</span>
								</el-option>
							</el-select>
						</el-form-item>
						<el-form-item prop="useCacheT" label="目标目录扫描缓存">
							<el-select v-model="editData.useCacheT" class="label_width">
								<el-option label="不使用" :value="0">
									<span class="option-left">不使用</span>
									<span class="option-right">如果会对目标目录手动操作，选这个，但更容易被网盘限制</span>
								</el-option>
								<el-option label="使用" :value="1">
									<span class="option-left">使用</span>
									<span class="option-right">推荐，降低网盘风控可能</span>
								</el-option>
							</el-select>
						</el-form-item>
						<el-form-item prop="scanIntervalT" label="目标目录操作间隔">
							<el-input v-model.number="editData.scanIntervalT" placeholder="目标目录操作间隔"
								class="label_width">
								<template slot="append">秒</template>
							</el-input>
						</el-form-item>
						<el-form-item prop="useCacheS" label="源目录扫描缓存">
							<el-select v-model="editData.useCacheS" class="label_width">
								<el-option label="不使用" :value="0">
									<span class="option-left">不使用</span>
									<span class="option-right">用这个</span>
								</el-option>
								<el-option label="使用" :value="1">
									<span class="option-left">使用</span>
									<span class="option-right">不要用，除非你知道自己在做什么</span>
								</el-option>
							</el-select>
						</el-form-item>
						<el-form-item prop="scanIntervalS" label="源目录操作间隔">
							<el-input v-model.number="editData.scanIntervalS" placeholder="源目录操作间隔" class="label_width">
								<template slot="append">秒</template>
							</el-input>
						</el-form-item>
						<el-form-item prop="possess" label="匹配项正则表达式">
							<el-input v-model="editData.possess" placeholder="匹配项正则表达式" class="label_width">
							</el-input>
						</el-form-item>
						<el-form-item prop="strm_nfo" label="刮削文件正则表达式" v-if="editData.method == 3">
							<el-input v-model="editData.strm_nfo" placeholder="strm刮削文件正则表达式"
								class="label_width">
							</el-input>
						</el-form-item>
						<el-form-item prop="exclude" label="排除项语法">
							<div class="label_width">类gitignore<br />
								<span @click="toIgnore" class="to-link">
									点击查看排除项简易教程
								</span>
							</div>
						</el-form-item>
						<el-form-item prop="exclude" label="排除项规则">
							<div class="label_width">
								<div class="label-list-box">
									<el-input v-model="excludeTmp" placeholder="输入后点添加才生效">
										<el-button slot="append" @click="addExclude">添加</el-button>
									</el-input>
									<div v-for="(item, index) in editData.exclude" class="label-list-item">
										<div class="bg-3 label-list-item-left">
											{{ item }}
										</div>
										<el-button type="danger" size="mini" @click="delExclude(index)">删除</el-button>
									</div>
								</div>
							</div>
						</el-form-item>
						<el-form-item prop="ignore_path" label="路径排除项语法">
							<div class="label_width">匹配规则目录开头路径下的所有文件及子文件夹,路径不带/开头为目录子路径</div>
						</el-form-item>
						<el-form-item prop="ignore_path" label="路径排除项规则">
							<div class="label_width">
								<div class="label-list-box">
									<el-input v-model="ignorePathTmp" placeholder="输入后点添加才生效">
										<el-button slot="append" @click="addIgnorePath">添加</el-button>
									</el-input>
									<div v-for="(item, index) in editData.ignore_path" class="label-list-item">
										<div class="bg-3 label-list-item-left">
											{{ item }}
										</div>
										<el-button type="danger" size="mini"
											@click="delIgnorePath(index)">删除</el-button>
									</div>
								</div>
							</div>
						</el-form-item>
						<el-form-item prop="strm_path" label="strm生成目录" v-if="editData.method == 3">
							<el-input v-model="editData.strm_path" placeholder="str生成目录" class="label_width">
							</el-input>
						</el-form-item>
						<el-form-item prop="strm_url_prefix" label="strm文件内容前缀" v-if="editData.method == 3">
							<el-input v-model="editData.strm_url_prefix" placeholder="strm文件内容前缀"
								class="label_width">
							</el-input>
						</el-form-item>
						<el-form-item prop="strm_src_sync" label="同步刮削文件到源目录" v-if="editData.method == 3">
							<div class="label_width">
								<el-switch v-model="editData.strm_src_sync" :active-value="1"
									:inactive-value="0"></el-switch>
							</div>
						</el-form-item>
						<el-form-item prop="strm_dst_sync" label="同步文件删除本地strm" v-if="editData.method == 3">
							<div class="label_width">
								<el-switch v-model="editData.strm_dst_sync" :active-value="1"
									:inactive-value="0"></el-switch>
							</div>
						</el-form-item>
						<el-form-item prop="strm_create_cover" label="覆盖本地strm文件" v-if="editData.method == 3">
							<div class="label_width">
								<el-switch v-model="editData.strm_create_cover" :active-value="1"
									:inactive-value="0"></el-switch>
							</div>
						</el-form-item>
						<el-form-item prop="strm_create_cover_possess" label="覆盖规则(源目录路径前缀)"
							v-if="editData.method == 3">
							<div class="label_width">
								<div class="label-list-box">
									<el-input v-model="strmCreateCoverPossessTmp" placeholder="输入后点添加才生效">
										<el-button slot="append" @click="addStrmCreateCoverPossess">添加</el-button>
									</el-input>
									<div v-for="(item, index) in editData.strm_create_cover_possess"
										class="label-list-item">
										<div class="bg-3 label-list-item-left">
											{{ item }}
										</div>
										<el-button type="danger" size="mini"
											@click="delStrmCreateCoverPossess(index)">删除</el-button>
									</div>
								</div>
							</div>
						</el-form-item>
						<el-form-item prop="strm_src_sync_cover" label="覆盖源目录刮削文件" v-if="editData.method == 3">
							<div class="label_width">
								<el-switch v-model="editData.strm_src_sync_cover" :active-value="1"
									:inactive-value="0"></el-switch>
							</div>
						</el-form-item>
						<el-form-item prop="strm_src_sync_cover_possess" label="覆盖刮削文件规则(源目录路径前缀)"
							v-if="editData.method == 3">
							<div class="label_width">
								<div class="label-list-box">
									<el-input v-model="strmSrcSyncCoverPossessTmp" placeholder="输入后点添加才生效">
										<el-button slot="append" @click="addStrmSrcSyncCoverPossess">添加</el-button>
									</el-input>
									<div v-for="(item, index) in editData.strm_src_sync_cover_possess"
										class="label-list-item">
										<div class="bg-3 label-list-item-left">
											{{ item }}
										</div>
										<el-button type="danger" size="mini"
											@click="delStrmSrcSyncCoverPossess(index)">删除</el-button>
									</div>
								</div>
							</div>
						</el-form-item>
						<!-- 飞牛配置选择 -->
						<el-form-item label="飞牛配置" v-if="editData.method == 3">
							<div class="label_width">
								<el-select v-model="pathMapping.feiniuId" placeholder="请选择飞牛配置"
									@change="handleFeiniuConfigChange">
									<el-option v-for="item in feiniuList" :key="item.id"
										:label="`${item.host} [${item.remark || item.username}]`"
										:value="item.id"></el-option>
								</el-select>
							</div>
						</el-form-item>
						<!-- 媒体库选择 -->
						<el-form-item label="媒体库" v-if="editData.method == 3 && pathMapping.feiniuId">
							<div class="label_width">
								<el-select v-model="pathMapping.media_library_id" placeholder="请选择媒体库">
									<el-option v-for="item in mediaLibraries" :key="item.guid" :label="`${item.title} (${item.guid})`"
										:value="item.guid"></el-option>
								</el-select>
							</div>
						</el-form-item>
						<!-- STRM路径 -->
						<el-form-item label="STRM路径" v-if="editData.method == 3">
							<div class="label_width">
								<el-input v-model="pathMapping.strm_path" placeholder="请输入STRM路径"></el-input>
							</div>
						</el-form-item>
						<!-- 飞牛映射路径 -->
						<el-form-item label="飞牛映射路径" v-if="editData.method == 3">
							<div class="label_width">
								<el-input v-model="pathMapping.media_path" placeholder="请输入飞牛映射路径"></el-input>
							</div>
						</el-form-item>
						<!-- 添加路径映射按钮 -->
						<el-form-item v-if="editData.method == 3">
							<div class="label_width">
								<el-button type="primary" @click="addPathMapping">添加路径映射</el-button>
							</div>
						</el-form-item>
						<!-- 路径映射列表 -->
						<el-form-item label="路径映射关系" v-if="editData.method == 3 && pathMappings.length > 0">
							<div class="label-width">
								<div v-for="(mapping, index) in pathMappings" class="label-list-item">
									<div class="bg-1 label-list-item-left mapping-content">
										{{ mapping.strm_path }} → {{ mapping.media_path }} (媒体库ID:
										{{ mapping.media_library_id }})
									</div>
									<el-button type="danger" size="mini" @click="delPathMapping(index)">删除</el-button>
								</div>
							</div>
						</el-form-item>
						<el-form-item v-if="editData.method == 2" class="warning-message-item">
	<div class="warning-message">移动模式存在风险，可能导致文件丢失（因为会删除源目录文件），该方法应仅用于不重要的文件或有多重备份的文件！希望你知道自己在做什么！</div>
</el-form-item>
						<el-form-item prop="isCron" label="调用方式">
							<el-select v-model="editData.isCron" class="label_width">
								<el-option label="间隔" :value="0">
									<span class="option-left">间隔</span>
									<span class="option-right">不推荐使用</span>
								</el-option>
								<el-option label="cron" :value="1">
									<span class="option-left">cron</span>
									<span class="option-right">推荐使用，有教程</span>
								</el-option>
								<el-option label="仅手动" :value="2">
									<span class="option-left">仅手动</span>
									<span class="option-right">不自动调用</span>
								</el-option>
							</el-select>
						</el-form-item>
						<template v-if="editData.isCron == 0">
							<el-form-item prop="interval" label="同步间隔">
								<el-input v-model.number="editData.interval" placeholder="请输入同步间隔" class="label_width">
									<template slot="append">分钟</template>
								</el-input>
							</el-form-item>
							<div class="interval-tip">间隔方式不会立即调用，如有需要，可在创建后立即手动调用</div>
						</template>
						<template v-else-if="editData.isCron == 1">
							<el-form-item prop="isCron" label="简易教程">
								<div class="label_width">
									<span @click="toCron" class="to-link">
										点击查看cron简易教程
									</span>
								</div>

							</el-form-item>
							<el-form-item v-for="item in cronList" :prop="item.label" :label="item.label" :key="item.label">
							<el-input v-model="editData[item.label]" :placeholder="item.palce" class="label_width">
							</el-input>
						</el-form-item>
						</template>
					</div>
				</el-form>
			</div>
			<span slot="footer" class="dialog-footer">
				<el-button @click="closeShow">取 消</el-button>
				<el-button type="primary" @click="submit" :loading="editLoading">确 定</el-button>
			</span>
		</el-dialog>
		<el-dialog :close-on-click-modal="false" :visible.sync="disableShow" :append-to-body="true" title="警告"
			width="460px" :before-close="closeDisableShow">
			<div class="warning-message">
				{{ disableIsDel ? '此操作不可逆，将永久删除该作业' : '将禁用任务' }}，确认吗？
			</div>
			<span slot="footer" class="dialog-footer">
				<el-button @click="closeDisableShow">取 消</el-button>
				<el-button type="primary" @click="submitDisable" :loading="editLoading">确 定</el-button>
			</span>
		</el-dialog>
		<pathSelect v-if="editData" :alistId="editData.alistId" ref="pathSelect" @submit="submitPath"></pathSelect>
	</div>
</template>

<script>
import {
	jobGetJob,
	jobPut,
	jobDelete,
	jobPost,
	alistGet
} from "@/api/job";
import {
	getFeiniuList,
	getFeiniuMediaLibraries
} from "@/api/feiniu";
import pathSelect from './components/pathSelect.vue';
import menuRefresh from './components/menuRefresh';
export default {
	name: 'Home',
	components: {
		pathSelect,
		menuRefresh
	},
	data() {
		return {
			jobData: {
				dataList: [],
				conut: 0
			},
			params: {
				pageSize: 10,
				pageNum: 1
			},
			alistList: [],
			cronList: [{
				label: 'year',
				palce: '2024'
			}, {
				label: 'month',
				palce: '1-12'
			}, {
				label: 'day',
				palce: '1-31'
			}, {
				label: 'week',
				palce: '1-53'
			}, {
				label: 'day_of_week',
				palce: '0-6 or mon,tue,wed,thu,fri,sat,sun'
			}, {
				label: 'hour',
				palce: '0-23'
			}, {
				label: 'minute',
				palce: '0-59'
			}, {
				label: 'second',
				palce: '0-59'
			}, {
				label: 'start_date',
				palce: '2000-01-01'
			}, {
				label: 'end_date',
				palce: '2040-12-31'
			}],
			cuIsSrc: false,
			loading: false,
			btnLoading: false,
			editLoading: false,
			editData: null,
			excludeTmp: '',
			ignorePathTmp: '',
			strmCreateCoverPossessTmp: '',
			strmSrcSyncCoverPossessTmp: '',
			editShow: false,
			disableShow: false,
			disableIsDel: false,
			disableCu: {
				id: null,
				pause: true,
				retry: null
			},
			feiniuList: [],
			mediaLibraries: [],
			pathMappings: [],
			pathMapping: {
				strm_path: '',
				feiniuId: '',
				media_library_id: '',
				media_path: ''
			},
			addRule: {
				srcPath: [{
					required: true,
					message: '请选择来源目录',
					trigger: 'change',
				}],
				dstPath: [{
					type: 'array',
					required: true,
					message: '请选择目标目录',
					trigger: 'change',
				}],
				alistId: [{
					type: 'number',
					required: true,
					message: '请选择引擎',
					trigger: 'change',
				}],
				scanIntervalT: [{
					required: true,
					pattern: /^(0|[1-9]\d*)$/,
					message: '必填且须为非负整数',
					trigger: 'blur',
				}],
				scanIntervalS: [{
					required: true,
					pattern: /^(0|[1-9]\d*)$/,
					message: '必填且须为非负整数',
					trigger: 'blur',
				}]
			}
		};
	},
	created() {
		this.getJobList();
	},
	beforeDestroy() { },
	methods: {
		runAllJob() {
			this.$confirm("确认执行所有未禁用的作业吗？", '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning'
			}).then(() => {
				this.btnLoading = true;
				jobPut({
					pause: null,
					retry: null
				}).then(res => {
					this.btnLoading = false;
					this.$message({
						message: res.msg,
						type: 'success'
					});
				}).catch(err => {
					this.btnLoading = false;
				})
			})
		},
		getJobList() {
			this.loading = true;
			jobGetJob(this.params).then(res => {
				this.loading = false;
				this.jobData = res.data;
			}).catch(err => {
				this.loading = false;
			})
		},
		selectPath(isSrc) {
			this.cuIsSrc = isSrc;
			this.$refs.pathSelect.show();
		},
		getAlistList() {
			alistGet().then(res => {
				this.alistList = res.data;
			})
		},
		getFeiniuList() {
			getFeiniuList().then(res => {
				this.feiniuList = res.data;
			})
		},
		handleFeiniuConfigChange(feiniuId) {
			// 清空相关数据
			//this.pathMapping.media_library_id = '';
			this.pathMapping.media_path = '';
			// 清空路径映射列表
			//this.pathMappings = [];
			// 获取新的媒体库列表
			if (feiniuId) {
				getFeiniuMediaLibraries(feiniuId).then(res => {
					this.mediaLibraries = res.data;
				})
			} else {
				this.mediaLibraries = [];
			}
		},
		getFeiniuMediaLibraries(feiniuId) {
			if (feiniuId) {
				getFeiniuMediaLibraries(feiniuId).then(res => {
					this.mediaLibraries = res.data;
				})
			} else {
				this.mediaLibraries = [];
			}
		},
		addPathMapping() {
			if (this.pathMapping.strm_path && this.pathMapping.feiniuId && this.pathMapping.media_library_id) {
				this.pathMappings.push({
					...this.pathMapping
				});
				// 保留飞牛ID和媒体库ID，方便继续添加映射
				this.pathMapping = {
					strm_path: '',
					feiniuId: this.pathMapping.feiniuId,
					media_library_id: this.pathMapping.media_library_id,
					media_path: ''
				};
			} else {
				this.$message.error('请填写完整的路径映射信息');
			}
		},
		delPathMapping(index) {
			this.pathMappings.splice(index, 1);
		},
		toCron() {
			window.open('https://blog.ctftools.com/2024/08/newpost-58/', '_blank');
		},
		toIgnore() {
			window.open('https://blog.ctftools.com/2024/09/newpost-60/', '_blank');
		},
		putJob(row, pause = null) {
			if (row.enable != 1 && pause !== false) {
				this.$message.error("如需手动执行，请先启用作业");
				return
			}
			this.btnLoading = true;
			jobPut({
				id: row.id,
				pause: pause,
				retry: null
			}).then(res => {
				this.btnLoading = false;
				this.$message({
					message: res.msg,
					type: 'success'
				});
				if (pause !== false) {
					this.detail(row.id);
				} else {
					this.getJobList();
				}
			}).catch(err => {
				this.btnLoading = false;
			})
		},
		copyJob(row, pause = null) {
			this.btnLoading = true;
			let data = JSON.parse(JSON.stringify(row));
			data.copy = '0'
			jobPost(data).then(res => {
				this.btnLoading = false;
				this.$message({
					message: res.msg,
					type: 'success'
				});
				this.getJobList();
			}).catch(err => {
				this.btnLoading = false;
			})
		},
		disableJobShow(row, disableIsDel) {
			this.disableIsDel = disableIsDel;
			this.disableCu.id = row.id;
			this.disableShow = true;
		},
		editJobShow(row) {
			if (row.enable && row.isCron != 2) {
				this.$message.error("禁用作业后才能编辑");
				return
			}
			if (this.alistList.length == 0) {
				this.getAlistList();
			}
			if (this.feiniuList.length == 0) {
				this.getFeiniuList();
			}
			this.excludeTmp = '';
			this.ignorePathTmp = '';
			this.strmCreateCoverPossessTmp = '';
			this.strmSrcSyncCoverPossessTmp = '';
			// 清空飞牛配置相关数据
			this.mediaLibraries = [];
			this.pathMapping = {
				strm_path: '',
				feiniuId: '',
				media_library_id: '',
				media_path: ''
			};
			this.editData = JSON.parse(JSON.stringify(row));
			this.editData.dstPath = this.editData.dstPath.split(':');
			if (this.editData.exclude) {
				this.editData.exclude = this.editData.exclude.split(':');
			} else {
				this.editData.exclude = [];
			}
			if (this.editData.ignore_path) {
				this.editData.ignore_path = this.editData.ignore_path.split(':');
			} else {
				this.editData.ignore_path = [];
			}
			if (this.editData.strm_create_cover_possess) {
				this.editData.strm_create_cover_possess = this.editData.strm_create_cover_possess.split(':');
			} else {
				this.editData.strm_create_cover_possess = [];
			}
			if (this.editData.strm_src_sync_cover_possess) {
				this.editData.strm_src_sync_cover_possess = this.editData.strm_src_sync_cover_possess.split(':');
			} else {
				this.editData.strm_src_sync_cover_possess = [];
			}
			// 初始化飞牛路径映射
			this.pathMappings = [];
			if (this.editData.strm_path_mapping) {
				// 解析strm_path_mapping字符串为对象数组
				const mappings = this.editData.strm_path_mapping.split('|');
				mappings.forEach(mapping => {
					const parts = mapping.split(':');
					if (parts.length === 3) {
						this.pathMappings.push({
							strm_path: parts[0],
							feiniuId: this.editData.feiniuId,
							media_library_id: parts[1],
							media_path: parts[2]
						});
					}
				});
			}
			// 如果有飞牛配置ID，设置到pathMapping中并加载媒体库
			if (this.editData.feiniuId) {
				this.pathMapping.feiniuId = this.editData.feiniuId;
				// 加载媒体库列表
				getFeiniuMediaLibraries(this.editData.feiniuId).then(res => {
					this.mediaLibraries = res.data;
				});
			}
			this.editShow = true;
		},
		addShow() {
			if (this.alistList.length == 0) {
				this.getAlistList();
			}
			if (this.feiniuList.length == 0) {
				this.getFeiniuList();
			}
			let editData = {
				enable: 1,
				remark: '',
				srcPath: '',
				dstPath: [],
				alistId: null,
				useCacheT: 1,
				scanIntervalT: 1,
				useCacheS: 0,
				scanIntervalS: 0,
				method: 0,
				interval: 1440,
				isCron: 0,
				exclude: [],
				possess: '',
				ignore_path: [],
				strm_nfo: '',
				strm_path: '',
				strm_url_prefix: '',
				strm_src_sync: 0,
				strm_dst_sync: 0,
				strm_create_cover: 0,
				strm_create_cover_possess: [],
				strm_src_sync_cover: 0,
				strm_src_sync_cover_possess: [],
				feiniuId: null,
				strm_path_mapping: ''
			}
			this.cronList.forEach(item => {
				editData[item.label] = null;
			})
			this.editData = editData;
			this.excludeTmp = '';
			this.ignorePathTmp = '';
			this.strmCreateCoverPossessTmp = '';
			this.strmSrcSyncCoverPossessTmp = '';
			// 清空飞牛配置相关数据
			this.mediaLibraries = [];
			// 初始化飞牛路径映射
			this.pathMappings = [];
			this.pathMapping = {
				strm_path: '',
				feiniuId: '',
				media_library_id: '',
				media_path: ''
			};
			this.editShow = true;
		},
		closeShow() {
			this.editShow = false;
			// 清空飞牛配置相关数据
			this.mediaLibraries = [];
			this.pathMappings = [];
			this.pathMapping = {
				strm_path: '',
				feiniuId: '',
				media_library_id: '',
				media_path: ''
			};
		},
		closeDisableShow() {
			this.disableShow = false;
			this.disableCu = {
				id: null,
				pause: true
			};
		},
		addExclude() {
			if (this.excludeTmp != '') {
				this.editData.exclude.push(this.excludeTmp);
			}
			this.excludeTmp = '';
		},
		delExclude(index) {
			this.editData.exclude.splice(index, 1);
		},
		addStrmSrcSyncCoverPossess() {
			if (this.strmSrcSyncCoverPossessTmp != '') {
				this.editData.strm_src_sync_cover_possess.push(this.strmSrcSyncCoverPossessTmp);
			}
			this.strmSrcSyncCoverPossessTmp = '';
		},
		delStrmSrcSyncCoverPossess(index) {
			this.editData.strm_src_sync_cover_possess.splice(index, 1);
		},
		addIgnorePath() {
			if (this.ignorePathTmp != '') {
				this.editData.ignore_path.push(this.ignorePathTmp);
			}
			this.ignorePathTmp = '';
		},
		delIgnorePath(index) {
			this.editData.ignore_path.splice(index, 1);
		},
		addStrmCreateCoverPossess() {
			if (this.strmCreateCoverPossessTmp != '') {
				this.editData.strm_create_cover_possess.push(this.strmCreateCoverPossessTmp);
			}
			this.strmCreateCoverPossessTmp = '';
		},
		delStrmCreateCoverPossess(index) {
			this.editData.strm_create_cover_possess.splice(index, 1);
		},
		delDstPath(index) {
			this.editData.dstPath.splice(index, 1);
		},
		submit() {
			this.$refs.jobRule.validate((valid) => {
				if (valid) {
					let postData = JSON.parse(JSON.stringify(this.editData));
					for (let i in postData) {
						if (postData[i] === '') {
							postData[i] = null;
						}
					}
					if (postData.isCron == 0 && postData.interval == null) {
						this.$message.error("选择间隔方式时，间隔必填");
						return
					}
					if (postData.isCron == 1) {
						let flag = 0;
						this.cronList.forEach(item => {
							if (postData[item.label] != null) {
								flag += 1;
							}
						})
						if (flag == 0) {
							this.$message.error("选择cron方式时，至少有一项不能为空");
							return
						}
					}
					if (postData.method == 3 && postData.strm_path == '') {
						this.$message.error("请添加strm文件生成路径");
						return
					}
					// 处理飞牛配置ID
					if (this.pathMappings.length > 0 && this.pathMappings[0].feiniuId) {
						postData.feiniuId = this.pathMappings[0].feiniuId;
					} else {
						postData.feiniuId = null;
					}

					// 处理飞牛路径映射关系
					if (this.pathMappings.length > 0) {
						// 将路径映射关系转换为字符串格式：strm_path:library_id:media_path|...
						postData.strm_path_mapping = this.pathMappings.map(mapping => {
							return `${mapping.strm_path}:${mapping.media_library_id}:${mapping.media_path}`;
						}).join('|');
					} else {
						postData.strm_path_mapping = null;
					}
					postData.dstPath = postData.dstPath.join(':');
					postData.exclude = postData.exclude.join(':');
					postData.ignore_path = postData.ignore_path.join(':');
					postData.strm_create_cover_possess = postData.strm_create_cover_possess.join(':');
					postData.strm_src_sync_cover_possess = postData.strm_src_sync_cover_possess.join(':');
					this.editLoading = true;
					jobPost(postData).then(res => {
						this.editLoading = false;
						this.$message({
							message: res.msg,
							type: 'success'
						});
						this.closeShow();
						this.getJobList();
					}).catch(err => {
						this.editLoading = false;
					})
				}
			})
		},
		submitDisable() {
			this.editLoading = true;
			if (this.disableIsDel) {
				jobDelete(this.disableCu).then(res => {
					this.editLoading = false;
					this.$message({
						message: res.msg,
						type: 'success'
					});
					this.getJobList();
					this.closeDisableShow();
				}).catch(err => {
					this.editLoading = false;
				})
			} else {
				jobPut(this.disableCu).then(res => {
					this.editLoading = false;
					this.$message({
						message: res.msg,
						type: 'success'
					});
					this.getJobList();
					this.closeDisableShow();
				}).catch(err => {
					this.editLoading = false;
				})
			}
		},
		submitPath(path) {
			if (this.cuIsSrc) {
				this.editData.srcPath = path;
			} else {
				if (this.editData.dstPath.includes(path)) {
					this.$message({
						message: '该目录已存在',
						type: 'error'
					});
				} else {
					this.editData.dstPath.push(path);
				}
			}
		},
		getMediaLibraryTitle(guid) {
			const library = this.mediaLibraries.find(item => item.guid === guid);
			return library ? library.title : guid;
		},
		detail(jobId) {
			this.$router.push({
				path: '/home/task',
				query: {
					jobId
				}
			})
		},
		handleSizeChange(val) {
			this.params.pageSize = val;
			this.getJobList();
		},
		handleCurrentChange(val) {
			this.params.pageNum = val;
			this.getJobList();
		}
	}
}
</script>

<style lang="scss">
.home {
	width: 100%;
	height: 100%;
	padding: 16px;
	box-sizing: border-box;
	color: var(--text-primary);
	// 在移动端调整内边距
	@media (max-width: 768px) {
		padding: 8px;
	}

	.top-box {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 16px;
		// 在移动端调整为垂直排列
		@media (max-width: 768px) {
			flex-direction: column;
			align-items: stretch;
			gap: 10px;
			margin-bottom: 10px;
		}

		.top-box-title {
			font-weight: bold;
			color: var(--text-primary);
			// 在移动端调整字体大小
			@media (max-width: 768px) {
				font-size: 18px;
			}
		}

		.top-box-left {
			display: flex;
			align-items: center;
			gap: 10px;
			// 在移动端调整为全屏宽度
			@media (max-width: 768px) {
				width: 100%;
				justify-content: space-between;
			}
		}
	}

	.pathList {
		display: flex;
		flex-wrap: wrap;
		flex-shrink: 0;

		.pathBox {
			font-size: 14px;
			padding: 2px 6px;
			margin: 2px 0;
			margin-right: 6px;
			border-radius: 3px;
			color: var(--text-primary);
			// 在移动端调整字体大小和内边距
			@media (max-width: 768px) {
				font-size: 12px;
				padding: 2px 4px;
				margin-right: 4px;
			}
		}

		.pathBox:last-child {
			margin-right: 0;
		}
	}

	.page {
		margin-top: 24px;
		display: flex;
		justify-content: center;
		// 在移动端调整间距
		@media (max-width: 768px) {
			margin-top: 16px;
		}
	}
	
	// 表格容器响应式处理
	.table-data {
		@media (max-width: 768px) {
			height: auto !important;
			overflow-x: auto;
		}
	}
}

.label_width {
	width: 100%;
	max-width: 240px;
	// 在移动端调整宽度
	@media (max-width: 768px) {
		width: 100%;
		max-width: 100%;
	}

	.label-list-box {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		min-height: 42px;
		// 在移动端调整最小高度
		@media (max-width: 768px) {
			min-height: 36px;
		}

		.label-list-item {
			display: flex;
			align-items: center;
			margin: 4px 0;
			margin-right: 12px;
			flex-shrink: 0;
			// 在移动端调整间距
			@media (max-width: 768px) {
				margin-right: 8px;
			}

			.label-list-item-left {
				border-radius: 3px;
				padding: 0 6px;
				line-height: 20px;
				margin-right: -4px;
				max-width: 180px;
				color: var(--text-primary);
				// 在移动端调整最大宽度和行高
				@media (max-width: 768px) {
					max-width: 120px;
					line-height: 18px;
					font-size: 12px;
				}
			}

			.el-button {
				margin-left: 10px;
				border-radius: 0 3px 3px 0;
				// 在移动端调整间距和大小
				@media (max-width: 768px) {
					margin-left: 6px;
					padding: 4px 8px;
					font-size: 12px;
				}
			}
		}
	}

	.to-link {
		color: var(--color-primary);
		text-decoration: underline;
		cursor: pointer;
		// 在移动端调整字体大小
		@media (max-width: 768px) {
			font-size: 12px;
		}
	}

	.option-left {
		float: left;
		margin-right: 16px;
	}

	.option-right {
		float: right;
		color: var(--text-secondary);
		font-size: 13px;
	}

	.interval-tip {
		grid-column: 1 / -1;
		margin: 10px 0;
		color: var(--text-secondary);
	}

	.warning-message {
	color: var(--color-danger) !important;
	font-weight: bold !important;
	text-align: center !important;
	font-size: 16px !important;
	margin: 20px 0 !important;
	line-height: 1.5 !important;
	width: 100% !important;
	max-width: 100% !important;
}
	
	.status-bg {
		width: 50px;
	}
}

.label_width_2 {
	width: 100%;
	max-width: 600px;
	// 在移动端调整宽度
	@media (max-width: 768px) {
		width: 100%;
		max-width: 100%;
	}
}

.elform-box {
	max-height: 70vh;
	overflow-y: auto;
	padding-right: 10px;
	// 在移动端调整最大高度和内边距
	@media (max-width: 768px) {
		max-height: 60vh;
		padding-right: 5px;
	}
}

.exclude-item {
	margin-right: 6px;
	padding: 0 2px;
	border-radius: 3px;
	color: var(--text-primary);
	// 在移动端调整间距和内边距
	@media (max-width: 768px) {
		margin-right: 4px;
		padding: 0 4px;
		font-size: 12px;
	}
}

.exclude-item:last-child {
	margin-right: 0;
}

/* 表单容器样式 */
.form-box {
	padding: 16px;
	background-color: var(--bg-secondary);
	border-radius: 8px;
	border: 1px solid var(--border-color);
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 表单分组样式 */
.form-section {
	margin-bottom: 24px;
	padding: 20px;
	background-color: var(--bg-quaternary);
	border-radius: 12px;
	border: 1px solid var(--border-light);
	transition: all 0.3s ease;
	
	&:hover {
		border-color: var(--color-primary);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}
}

.section-title {
	margin: 0 0 16px 0;
	font-size: 18px;
	font-weight: 600;
	color: var(--text-primary);
	border-bottom: 2px solid var(--color-primary);
	padding-bottom: 8px;
	display: flex;
	align-items: center;
	gap: 8px;
	
	&::before {
		content: '';
		display: inline-block;
		width: 4px;
		height: 20px;
		background-color: var(--color-primary);
		border-radius: 2px;
	}
}

/* 表单项样式 */
.form-box-item {
	margin-bottom: 16px;
	display: grid;
	grid-template-columns: 180px 1fr;
	align-items: flex-start;
	gap: 16px;
	
	&:last-child {
		margin-bottom: 0;
	}
}

.form-box-item-label {
	font-weight: 500;
	color: var(--text-primary);
	font-size: 14px;
	line-height: 20px;
	padding-top: 2px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.form-box-item-value {
	color: var(--text-secondary);
	font-size: 14px;
	line-height: 20px;
	word-break: break-all;
}

/* 文本截断样式 */
.text-truncate {
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 500px;
	display: inline-block;
	vertical-align: middle;
}

/* 排除项样式 */
.exclude-item {
	margin-right: 8px;
	margin-bottom: 8px;
	padding: 4px 12px;
	border-radius: 16px;
	background-color: var(--bg-tertiary);
	color: var(--text-primary);
	border: 1px solid var(--border-light);
	font-size: 13px;
	display: inline-block;
	transition: all 0.2s ease;
	
	&:hover {
		background-color: var(--bg-quinary);
		border-color: var(--color-primary);
		transform: translateY(-1px);
	}
}

/* 路径映射项样式 */
.path-mapping-item {
	display: flex;
	align-items: flex-start;
	padding: 12px 16px;
	background-color: var(--bg-tertiary);
	border-radius: 8px;
	margin-bottom: 12px;
	border: 1px solid var(--border-light);
	transition: all 0.2s ease;
	
	&:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}
	
	&:last-child {
		margin-bottom: 0;
	}
}

.mapping-index {
	margin-right: 12px;
	font-weight: 600;
	color: var(--color-primary);
	min-width: 24px;
	text-align: center;
	background-color: rgba(255, 255, 255, 0.1);
	padding: 2px 8px;
	border-radius: 12px;
	font-size: 13px;
}

.mapping-content {
	display: flex;
	flex-direction: column;
	flex: 1;
	gap: 6px;
}

.mapping-src,
.mapping-dst {
	max-width: 100%;
	font-size: 13px;
	color: var(--text-primary);
}

.mapping-arrow {
	margin: 0 8px;
	color: var(--text-tertiary);
	font-size: 14px;
	font-weight: bold;
}

.mapping-library {
	font-size: 12px;
	color: var(--text-tertiary);
	margin-left: 0;
	padding: 2px 8px;
	background-color: rgba(0, 0, 0, 0.05);
	border-radius: 4px;
	align-self: flex-start;
}

/* 操作按钮样式 */
.operation-buttons {
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
	padding: 12px 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
	.form-box-item {
		grid-template-columns: 150px 1fr;
		gap: 12px;
	}
	
	.text-truncate {
		max-width: 350px;
	}
}

@media (max-width: 768px) {
	.form-box {
		padding: 12px;
	}
	
	.form-section {
		padding: 16px;
		margin-bottom: 16px;
	}
	
	.section-title {
		font-size: 16px;
		margin-bottom: 12px;
	}
	
	.form-box-item {
		grid-template-columns: 1fr;
		gap: 8px;
	}
	
	.form-box-item-label {
		font-weight: 600;
		color: var(--color-primary);
		padding-top: 0;
	}
	
	.text-truncate {
		max-width: 100%;
	}
	
	.path-mapping-item {
		padding: 8px 12px;
		flex-direction: column;
		gap: 8px;
	}
	
	.mapping-index {
		align-self: flex-start;
	}
	
	.mapping-content {
		flex-direction: column;
		gap: 4px;
	}
	
	.mapping-src,
	.mapping-dst {
		max-width: 100%;
	}
	
	.mapping-arrow {
		display: none;
	}
	
	.exclude-item {
		margin-right: 6px;
		margin-bottom: 6px;
		padding: 3px 10px;
		font-size: 12px;
	}
}

/* 作业详情容器 */
.job-detail {
	padding: 16px;
	background-color: var(--bg-secondary);
	border-radius: 8px;
	border: 1px solid var(--border-color);
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 基本信息卡片 */
.info-card {
	background-color: var(--bg-quaternary);
	border-radius: 12px;
	border: 1px solid var(--border-light);
	padding: 20px;
	margin-bottom: 24px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	transition: all 0.3s ease;
	
	&:hover {
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}
}

.info-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16px;
}

.info-title {
	font-size: 20px;
	font-weight: 600;
	color: var(--text-primary);
	margin: 0;
}

.job-status {
	padding: 4px 12px;
	border-radius: 16px;
	font-size: 13px;
	font-weight: 500;
	
	&.enabled {
		background-color: rgba(82, 196, 26, 0.1);
		color: var(--color-success);
		border: 1px solid var(--color-success);
	}
	
	&.disabled {
		background-color: rgba(250, 128, 114, 0.1);
		color: var(--color-danger);
		border: 1px solid var(--color-danger);
	}
}

.info-content {
	padding-top: 16px;
	border-top: 1px solid var(--border-light);
}

.info-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
	gap: 16px;
}

.info-item {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.info-label {
	font-size: 13px;
	color: var(--text-secondary);
	font-weight: 500;
}

.info-value {
	font-size: 14px;
	color: var(--text-primary);
	font-weight: 400;
}

/* 方法标签 */
.method-tag {
	padding: 3px 10px;
	border-radius: 12px;
	font-size: 12px;
	font-weight: 500;
	
	&.method-0 {
		background-color: rgba(82, 196, 26, 0.1);
		color: var(--color-success);
		border: 1px solid rgba(82, 196, 26, 0.3);
	}
	
	&.method-1 {
		background-color: rgba(247, 186, 42, 0.1);
		color: var(--color-warning);
		border: 1px solid rgba(247, 186, 42, 0.3);
	}
	
	&.method-2 {
		background-color: rgba(245, 108, 108, 0.1);
		color: var(--color-danger);
		border: 1px solid rgba(245, 108, 108, 0.3);
	}
	
	&.method-3 {
		background-color: rgba(144, 147, 153, 0.1);
		color: var(--color-info);
		border: 1px solid rgba(144, 147, 153, 0.3);
	}
}

/* Cron标签 */
.cron-tag {
	padding: 3px 10px;
	border-radius: 12px;
	font-size: 12px;
	font-weight: 500;
	
	&.cron-0 {
		background-color: rgba(82, 196, 26, 0.1);
		color: var(--color-success);
		border: 1px solid rgba(82, 196, 26, 0.3);
	}
	
	&.cron-1 {
		background-color: rgba(247, 186, 42, 0.1);
		color: var(--color-warning);
		border: 1px solid rgba(247, 186, 42, 0.3);
	}
	
	&.cron-2 {
		background-color: rgba(144, 147, 153, 0.1);
		color: var(--color-info);
		border: 1px solid rgba(144, 147, 153, 0.3);
	}
}

/* 配置区域 */
.config-section {
	margin-bottom: 24px;
}

.section-title {
	font-size: 18px;
	font-weight: 600;
	color: var(--text-primary);
	margin-bottom: 20px;
	display: flex;
	align-items: center;
	gap: 10px;
	padding-bottom: 10px;
	border-bottom: 2px solid var(--color-primary);
}

.section-icon {
	color: var(--color-primary);
}

/* 配置卡片 */
.config-card {
	background-color: var(--bg-quaternary);
	border-radius: 12px;
	border: 1px solid var(--border-light);
	padding: 20px;
	margin-bottom: 20px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	transition: all 0.3s ease;
	
	&:hover {
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
		border-color: var(--color-primary);
	}
}

.config-header {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 16px;
	padding-bottom: 12px;
	border-bottom: 1px solid var(--border-light);
}

.config-icon {
	color: var(--color-primary);
	width: 16px;
	height: 16px;
}

.config-title {
	font-size: 16px;
	font-weight: 500;
	color: var(--text-primary);
}

.config-content {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

/* 配置网格 */
.config-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
	gap: 16px;
}

.config-item {
	display: flex;
	flex-direction: column;
	gap: 6px;
	
	&.full-width {
		grid-column: 1 / -1;
	}
}

.config-label {
	font-size: 14px;
	font-weight: 500;
	color: var(--text-primary);
}

.config-value {
	font-size: 14px;
	color: var(--text-secondary);
	word-break: break-all;
	
	&.code {
		background-color: rgba(0, 0, 0, 0.05);
		border: 1px solid var(--border-light);
		border-radius: 6px;
		padding: 8px 12px;
		font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
		font-size: 13px;
		line-height: 1.5;
	}
	
	&.toggle {
		padding: 2px 8px;
		border-radius: 12px;
		font-size: 13px;
		font-weight: 500;
		
		&.on {
			background-color: rgba(82, 196, 26, 0.1);
			color: var(--color-success);
			border: 1px solid var(--color-success);
		}
		
		&.off {
			background-color: rgba(250, 128, 114, 0.1);
			color: var(--color-danger);
			border: 1px solid var(--color-danger);
		}
	}
}

/* 标签列表 */
.tag-list {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	align-items: center;
}

.tag {
	padding: 4px 12px;
	background-color: var(--bg-tertiary);
	color: var(--text-primary);
	border: 1px solid var(--border-light);
	border-radius: 16px;
	font-size: 13px;
	transition: all 0.2s ease;
	
	&:hover {
		background-color: var(--bg-quinary);
		border-color: var(--color-primary);
		transform: translateY(-1px);
	}
}

/* 空值样式 */
.empty {
	color: var(--text-tertiary);
	font-style: italic;
	font-size: 14px;
}

/* Cron配置 */
.cron-config {
	display: flex;
	flex-wrap: wrap;
	gap: 12px;
	align-items: center;
}

.cron-item {
	display: flex;
	align-items: center;
	gap: 4px;
	font-size: 14px;
}

.cron-label {
	font-weight: 500;
	color: var(--text-primary);
}

.cron-value {
	color: var(--text-secondary);
}

/* 路径映射 */
.mapping-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.mapping-item {
	background-color: var(--bg-tertiary);
	border: 1px solid var(--border-light);
	border-radius: 8px;
	padding: 12px;
	transition: all 0.2s ease;
	
	&:hover {
		border-color: var(--color-primary);
		transform: translateY(-1px);
	}
}

.mapping-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8px;
}

.mapping-index {
	font-weight: 600;
	color: var(--color-primary);
	background-color: rgba(255, 255, 255, 0.1);
	padding: 2px 8px;
	border-radius: 12px;
	font-size: 13px;
}

.mapping-media-library {
	font-size: 13px;
	color: var(--text-secondary);
}

.mapping-content {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-wrap: wrap;
}

.mapping-src,
.mapping-dst {
	font-size: 13px;
	color: var(--text-primary);
	max-width: 100%;
	word-break: break-all;
}

.mapping-arrow {
	color: var(--text-tertiary);
	font-weight: bold;
	font-size: 14px;
}

/* 操作按钮栏 */
.action-bar {
	display: flex;
	gap: 12px;
	justify-content: flex-start;
	align-items: center;
	padding-top: 16px;
	border-top: 1px solid var(--border-light);
}

.action-bar .el-button {
	border-radius: 6px;
	font-weight: 500;
	transition: all 0.3s ease;
	
	&:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
}

/* 响应式设计 */
@media (max-width: 768px) {
	.info-grid,
	.config-grid {
		grid-template-columns: 1fr;
	}
	
	.info-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 12px;
	}
	
	.action-bar {
		flex-wrap: wrap;
	}
}

/* 清除默认样式 */
.form-box,
.form-section,
.form-box-item,
.form-box-item-label,
.form-box-item-value {
	all: unset;
	box-sizing: border-box;
}

.form-box {
	display: block;
}

.form-section {
	display: block;
}

.form-box-item {
	display: block;
}

.form-box-item-label {
	display: block;
}

.form-box-item-value {
	display: block;
}

/* 编辑弹框容器样式 */
.elform-box {
	max-height: 70vh;
	overflow-y: auto;
	padding-right: 10px;
	/* 在移动端调整最大高度和内边距 */
	@media (max-width: 768px) {
		max-height: 60vh;
		padding-right: 5px;
	}
}

/* 编辑弹框网格布局 */
.grid-layout {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 24px;
	align-items: start;
	padding: 16px 0;
}

/* 确保表单项占满网格单元格 */
.grid-layout .el-form-item {
	margin-bottom: 0;
	transition: all 0.3s ease;
}

/* 表单项标签样式优化 */
.grid-layout .el-form-item__label {
	font-weight: 600;
	color: var(--text-primary);
	font-size: 14px;
	line-height: 38px;
	padding-bottom: 0;
	text-align: right;
	vertical-align: middle;
}

/* 表单项内容中心对齐 */
.grid-layout .el-form-item__content {
	vertical-align: middle;
	line-height: 38px;
}

/* 输入框宽度优化 */
.grid-layout .label_width {
	width: 100%;
	max-width: 100%;
}

/* 开关组件对齐优化 */
.grid-layout .el-switch {
	margin-top: 0;
	vertical-align: middle;
}

/* 按钮组件对齐优化 */
.grid-layout .el-button {
	margin-top: 0;
	vertical-align: middle;
}

/* 选择框对齐优化 */
.grid-layout .el-select {
	vertical-align: middle;
}

/* 输入框对齐优化 */
.grid-layout .el-input {
	vertical-align: middle;
}

/* 警告消息项样式 */
.grid-layout .warning-message-item {
	grid-column: 1 / -1;
	margin-bottom: 16px;
	padding: 12px 16px;
	background-color: rgba(250, 128, 114, 0.1);
	border: 1px solid rgba(250, 128, 114, 0.3);
	border-radius: 8px;
}

/* 警告消息文本样式 */
.warning-message {
	color: var(--color-danger);
	font-size: 14px;
	line-height: 1.5;
	font-weight: 500;
	text-align: left;
}

/* 路径映射相关表单项的特殊处理 */
.grid-layout .el-form-item:nth-child(n+44) {
	grid-column: span 1;
}

/* 表单分组样式 */
.form-group {
	grid-column: 1 / -1;
	margin: 24px 0 16px;
	padding: 16px;
	background-color: var(--bg-tertiary);
	border: 1px solid var(--border-light);
	border-radius: 12px;
}

.form-group-title {
	font-size: 16px;
	font-weight: 600;
	color: var(--color-primary);
	margin: 0 0 8px 0;
	padding-bottom: 8px;
	border-bottom: 2px solid var(--color-primary);
}

.form-group-description {
	font-size: 13px;
	color: var(--text-secondary);
	margin: 0;
	line-height: 1.4;
}

/* 间隔提示样式优化 */
.interval-tip {
	grid-column: 2;
	margin-top: 8px;
	font-size: 12px;
	color: var(--text-secondary);
	line-height: 1.4;
}

/* 链接样式优化 */
.to-link {
	color: var(--color-primary);
	text-decoration: underline;
	cursor: pointer;
	transition: all 0.3s ease;
	font-size: 13px;
	
	&:hover {
		color: var(--color-primary-dark);
		text-decoration: none;
	}
}

/* 标签列表样式优化 */
.label-list-box {
	min-height: 42px;
	padding: 8px 0;
}

.label-list-item {
	margin: 6px 12px 6px 0;
	transition: all 0.3s ease;
	
	&:hover {
		transform: translateY(-1px);
	}
}

.label-list-item-left {
	padding: 4px 10px;
	border-radius: 6px;
	font-size: 13px;
	line-height: 1.4;
	margin-right: 6px;
}

/* 响应式设计 - 编辑弹框 */
@media (max-width: 768px) {
	.grid-layout {
		grid-template-columns: 1fr;
		gap: 16px;
		padding: 8px 0;
	}
	
	.grid-layout .el-form-item:nth-child(n+44) {
		grid-column: span 1;
	}
	
	.form-group {
		margin: 16px 0 8px;
		padding: 12px;
	}
	
	.form-group-title {
		font-size: 14px;
	}
	
	.interval-tip {
		grid-column: 1;
		margin-top: 4px;
	}
}

/* 滚动条样式优化 */
.elform-box::-webkit-scrollbar {
	width: 8px;
}

.elform-box::-webkit-scrollbar-track {
	background: var(--bg-tertiary);
	border-radius: 4px;
}

.elform-box::-webkit-scrollbar-thumb {
	background: var(--border-color);
	border-radius: 4px;
	
	&:hover {
		background: var(--border-dark);
	}
}

/* 表单元素交互优化 */
.grid-layout .el-input__inner,
.grid-layout .el-select__input,
.grid-layout .el-textarea__inner {
	transition: all 0.3s ease;
	border-radius: 6px;
}

.grid-layout .el-input__inner:focus,
.grid-layout .el-select__input.is-focus,
.grid-layout .el-textarea__inner:focus {
	border-color: var(--color-primary);
	box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 按钮样式优化 */
.grid-layout .el-button {
	border-radius: 6px;
	transition: all 0.3s ease;
	
	&:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
}

/* 选择框选项样式优化 */
.grid-layout .el-select-dropdown__item {
	transition: all 0.2s ease;
	
	&:hover {
		background-color: var(--bg-tertiary);
	}
}

/* 配置项分组标题 */
.config-group-title {
	grid-column: 1 / -1;
	margin: 20px 0 12px;
	padding: 8px 0;
	font-size: 16px;
	font-weight: 600;
	color: var(--color-primary);
	border-bottom: 2px solid var(--color-primary);
}
</style>
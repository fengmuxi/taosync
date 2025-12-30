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
					<div class="form-box">
						<!-- 基本配置 -->
						<div class="form-section">
							<h4 class="section-title">基本配置</h4>
							<div class="form-box-item">
								<div class="form-box-item-label">
									同步方式
								</div>
								<div class="form-box-item-value">
									{{ props.row.method == 0 ? '仅新增' : (props.row.method == 1 ? '全同步' : (props.row.method == 2
										? '移动模式' : 'strm模式'))}}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									调用方式
								</div>
								<div class="form-box-item-value">
									{{ props.row.isCron == 0 ? '间隔' : (props.row.isCron == 1 ? 'cron' : '仅手动') }}
								</div>
							</div>
							<div class="form-box-item" v-if="props.row.isCron == 0">
								<div class="form-box-item-label">
									同步间隔
								</div>
								<div class="form-box-item-value">
									{{ props.row.interval }} 分钟
								</div>
							</div>
							<template v-else-if="props.row.isCron == 1">
								<div class="form-box-item" v-for="item in cronList" :key="item.label">
									<div class="form-box-item-label">
										{{ item.label }}
									</div>
									<div class="form-box-item-value">
										{{ props.row[item.label] || '-' }}
									</div>
								</div>
							</template>
						</div>

						<!-- 扫描配置 -->
						<div class="form-section">
							<h4 class="section-title">扫描配置</h4>
							<div class="form-box-item">
								<div class="form-box-item-label">
									目标目录扫描
								</div>
								<div class="form-box-item-value">
									{{ props.row.useCacheT == 0 ? '不用缓存' : '使用缓存' }}，操作间隔为 {{ props.row.scanIntervalT }} 秒
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									源目录扫描
								</div>
								<div class="form-box-item-value">
									{{ props.row.useCacheS == 0 ? '不用缓存' : '使用缓存' }}，操作间隔为 {{ props.row.scanIntervalS }} 秒
								</div>
							</div>
						</div>

						<!-- 匹配规则 -->
						<div class="form-section">
							<h4 class="section-title">匹配规则</h4>
							<div class="form-box-item">
								<div class="form-box-item-label">
									文件匹配正则
								</div>
								<div class="form-box-item-value text-truncate">
									{{ props.row.possess || '-' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									排除项规则
								</div>
								<div class="form-box-item-value">
									<span v-if="props.row.exclude == null">-</span>
									<template v-else>
										<span class="exclude-item bg-3" v-for="item in props.row.exclude.split(':')" :key="item">
											{{ item }}
										</span>
									</template>
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									路径排除项规则
								</div>
								<div class="form-box-item-value">
									<span v-if="props.row.ignore_path == null">-</span>
									<template v-else>
										<span class="exclude-item bg-3" v-for="item in props.row.ignore_path.split(':')" :key="item">
											{{ item }}
										</span>
									</template>
								</div>
							</div>
						</div>

						<!-- strm模式配置 -->
						<div class="form-section" v-if="props.row.method == 3">
							<h4 class="section-title">strm模式配置</h4>
							<div class="form-box-item">
								<div class="form-box-item-label">
									刮削文件匹配正则
								</div>
								<div class="form-box-item-value text-truncate">
									{{ props.row.strm_nfo || '-' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									strm文件保存路径
								</div>
								<div class="form-box-item-value text-truncate">
									{{ props.row.strm_path || '-' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									strm文件内容前缀
								</div>
								<div class="form-box-item-value text-truncate">
									{{ props.row.strm_url_prefix || '-' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									同步刮削文件到源目录
								</div>
								<div class="form-box-item-value">
									{{ props.row.strm_src_sync == 0 ? '否' : '是' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									同步文件删除本地strm
								</div>
								<div class="form-box-item-value">
									{{ props.row.strm_dst_sync == 0 ? '否' : '是' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									覆盖本地strm文件
								</div>
								<div class="form-box-item-value">
									{{ props.row.strm_create_cover == 0 ? '否' : '是' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									覆盖源目录刮削文件
								</div>
								<div class="form-box-item-value">
									{{ props.row.strm_src_sync_cover == 0 ? '否' : '是' }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									覆盖规则(源目录路径前缀)
								</div>
								<div class="form-box-item-value">
									<span v-if="props.row.strm_create_cover_possess == null">-</span>
									<template v-else>
										<span class="exclude-item bg-3" v-for="item in props.row.strm_create_cover_possess.split(':')" :key="item">
											{{ item }}
										</span>
									</template>
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-label">
									覆盖刮削文件规则(源目录路径前缀)
								</div>
								<div class="form-box-item-value">
									<span v-if="props.row.strm_src_sync_cover_possess == null">-</span>
									<template v-else>
										<span class="exclude-item bg-3" v-for="item in props.row.strm_src_sync_cover_possess.split(':')" :key="item">
											{{ item }}
										</span>
									</template>
								</div>
							</div>
							<!-- <div class="form-box-item">
								<div class="form-box-item-label">
									飞牛配置
								</div>
								<div class="form-box-item-value text-truncate">
									<template v-if="props.row.feiniuId">
										<span v-for="item in feiniuList" :key="item.id"
											v-if="item.id == props.row.feiniuId">
											{{ `${item.host} [${item.remark || item.username}]` }}
										</span>
									</template>
									<span v-else>-</span>
								</div>
							</div> -->
							<div class="form-box-item">
								<div class="form-box-item-label">
									路径映射关系
								</div>
								<div class="form-box-item-value">
									<span v-if="!props.row.strm_path_mapping">-</span>
									<template v-else>
										<div v-for="(mapping, index) in props.row.strm_path_mapping.split('|')"
										class="path-mapping-item bg-3" :key="index">
											<div class="mapping-index">{{ index + 1 }}.</div>
											<div class="mapping-content">
												<span class="mapping-src text-truncate">{{ mapping.split(':')[0] }}</span>
												<span class="mapping-arrow">→</span>
												<span class="mapping-dst text-truncate">{{ mapping.split(':')[2] }}</span>
												<span class="mapping-library">(媒体库: {{ getMediaLibraryTitle(mapping.split(':')[1]) }})</span>
											</div>
										</div>
									</template>
								</div>
							</div>
						</div>

						<!-- 创建时间和操作按钮 -->
						<div class="form-section">
							<h4 class="section-title">其他</h4>
							<div class="form-box-item">
								<div class="form-box-item-label">
									创建时间
								</div>
								<div class="form-box-item-value">
									{{ props.row.createTime | timeStampFilter }}
								</div>
							</div>
							<div class="form-box-item">
								<div class="form-box-item-value operation-buttons">
									<template v-if="props.row.isCron != 2">
										<el-button type="warning" :loading="btnLoading" size="mini" v-if="props.row.enable"
											@click="disableJobShow(props.row, false)">禁用</el-button>
										<el-button type="success" :loading="btnLoading" size="mini" v-else
											@click="putJob(props.row, false)">启用</el-button>
									</template>
									<el-button type="danger" :loading="btnLoading" size="mini"
										@click="disableJobShow(props.row, true)">删除</el-button>
									<el-button type="primary" :loading="btnLoading" size="mini"
										@click="editJobShow(props.row)">编辑</el-button>
								</div>
							</div>
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
						<span v-if="editData.method == 2" class="form-warning-message">移动模式存在风险，可能导致文件丢失（因为会删除源目录文件），该方法应仅用于不重要的文件或有多重备份的文件！希望你知道自己在做什么！</span>
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

/* 表单分组样式 */
.form-section {
	margin-bottom: 20px;
	padding: 12px;
	background-color: var(--bg-quaternary);
	border-radius: 6px;
	border: 1px solid var(--border-light);
}

.section-title {
	margin: 0 0 12px 0;
	font-size: 16px;
	font-weight: bold;
	color: var(--text-primary);
	border-bottom: 1px solid var(--border-light);
	padding-bottom: 6px;
}

/* 文本截断样式 */
.text-truncate {
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 400px;
	display: inline-block;
	vertical-align: middle;
}

/* 路径映射项样式 */
.path-mapping-item {
			display: flex;
			align-items: center;
			justify-content: space-between;
			padding: 8px 12px;
			background-color: var(--bg-secondary);
			border-radius: 4px;
			margin-bottom: 8px;
		}

		.grid-layout {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 16px;
		}

		.option-left {
			float: left;
			margin-right: 16px;
		}

		.option-right {
			float: right;
			color: #7b9dad;
			font-size: 13px;
		}

		.label-list-item {
			margin-bottom: 8px;
		}

		.label-width {
			min-height: 100px;
		}

		.form-warning-message {
			margin-top: -12px;
			margin-left: 410px;
			margin-bottom: 18px;
			color: #f56c6c;
			font-weight: bold;
		}

		.no-margin {
			margin-left: 0;
		}

		.mapping-content {
			max-width: 400px;
		}

.mapping-index {
	margin-right: 8px;
	font-weight: bold;
	min-width: 20px;
}

.mapping-content {
	display: flex;
	align-items: center;
	flex: 1;
	flex-wrap: wrap;
	gap: 8px;
}

.mapping-src,
.mapping-dst {
	max-width: 200px;
}

.mapping-arrow {
	margin: 0 4px;
	color: var(--text-secondary);
}

.mapping-library {
	font-size: 12px;
	color: var(--text-tertiary);
	margin-left: 8px;
	flex-basis: 100%;
	margin-top: 2px;
}

/* 操作按钮样式 */
.operation-buttons {
	display: flex;
	gap: 8px;
	flex-wrap: wrap;
}

/* 响应式调整 */
@media (max-width: 768px) {
	.text-truncate {
		max-width: 200px;
	}
	
	.mapping-src,
	.mapping-dst {
		max-width: 120px;
	}
	
	.form-section {
		padding: 8px;
		margin-bottom: 12px;
	}
	
	.section-title {
		font-size: 14px;
		margin-bottom: 8px;
	}
	
	.path-mapping-item {
		padding: 2px 4px;
	}
}
</style>
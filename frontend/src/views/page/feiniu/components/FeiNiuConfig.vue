<template>
  <div class="feiniu-config">
    <div class="card-box">
      <el-card v-for="(item, index) in feiniuList" :key="index" class="card-item">
        <div class="card-item-content" @click="editShowDialog(item)">
          <div class="card-item-top">
            <el-image src="/flyniu.svg" fit="contain" style="width: 60px;height: 60px;"></el-image>
            <div class="card-item-user">
              <div class="card-item-name">{{item.username}}</div>
              <div class="card-item-status" :class="item.enable == 1 ? 'enabled' : 'disabled'">
                {{item.enable == 1 ? '已启用' : '已禁用'}}
              </div>
            </div>
          </div>
          <div class="card-item-host" :title="item.host">{{item.host}}</div>
          <div class="card-item-info">
            <div class="info-item" v-if="item.remark">
              <span class="label">备注:</span>
              <span class="value remark" :title="item.remark">{{item.remark}}</span>
            </div>
            <div class="info-item placeholder" v-else></div>
          </div>
          <div class="card-item-bottom">
            <el-button size="small" type="primary" @click.stop="editShowDialog(item)">编辑</el-button>
            <el-button size="small" type="info" @click.stop="testConnectionOnItem(item)">测试连接</el-button>
            <el-button size="small" type="danger" @click.stop="delFeiniu(item.id)">删除</el-button>
          </div>
        </div>
      </el-card>
      <div class="card-item card-add" @click="addShow" v-if="!getLoading">
        <template v-if="feiniuList.length == 0">
          暂无飞牛配置，请<span class="highlight-text">新增</span>
        </template>
        <span v-else>新增</span>
      </div>
    </div>
    
    <!-- 编辑/新增对话框 -->
    <el-dialog :close-on-click-modal="false" :visible.sync="editShow" :title="editFlag ? '编辑飞牛配置' : '新增飞牛配置'" width="600px"
      :before-close="closeShow" :append-to-body="true">
      <div class="elform-box">
        <el-form :model="editData" :rules="editFlag ? editRule : addRule" ref="addRule" v-if="editShow"
          label-width="120px" size="medium">

          <el-form-item prop="host" label="服务器地址">
            <el-input v-model="editData.host" placeholder="请输入飞牛服务器地址，如：http://192.168.1.100:8005">
              <i slot="prefix" class="el-icon-link"></i>
            </el-input>
          </el-form-item>
          <el-form-item prop="username" label="用户名">
            <el-input v-model="editData.username" placeholder="请输入飞牛用户名">
              <i slot="prefix" class="el-icon-user"></i>
            </el-input>
          </el-form-item>
          <el-form-item prop="password" label="密码">
            <el-input v-model="editData.password" type="password" placeholder="请输入密码，编辑时留空表示不修改">
              <i slot="prefix" class="el-icon-lock"></i>
            </el-input>
            <div class="form-tip" v-if="editFlag">💡 提示：编辑时密码留空表示不修改原密码</div>
          </el-form-item>

          <el-form-item label="启用状态">
            <el-switch v-model="editData.enable" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用"></el-switch>
          </el-form-item>
          <el-form-item prop="remark" label="备注信息">
            <el-input v-model="editData.remark" placeholder="请输入备注信息（可选）">
              <i slot="prefix" class="el-icon-document"></i>
            </el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="closeShow" size="medium">取 消</el-button>
        <el-button type="info" @click="testConnection" :loading="testLoading" size="medium">测试连接</el-button>
        <el-button type="primary" @click="submit" :loading="editLoading" size="medium">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getFeiniuList, postAddFeiniu, putEditFeiniu, delFeiniu } from '@/api/feiniu'
import { ElMessage } from 'element-ui'
import request from '@/utils/request'

export default {
  name: 'FeiNiuConfigComponent',
  components: {},
  data() {
    return {
      feiniuList: [],
      getLoading: false,
      deleteLoading: false,
      editLoading: false,
      testLoading: false,
      editData: null,
      editFlag: false,
      editShow: false,
      editRule: {
        host: [
          { required: true, message: '请输入飞牛服务器地址', trigger: 'blur' }
        ],
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ]
      },
      addRule: {
        host: [
          { required: true, message: '请输入飞牛服务器地址', trigger: 'blur' }
        ],
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    };
  },
  created() {
    this.getFeiniuList();
  },
  methods: {
    getFeiniuList() {
      this.getLoading = true;
      getFeiniuList().then(res => {
        this.getLoading = false;
        this.feiniuList = res.data;
      }).catch(err => {
        this.getLoading = false;
      })
    },
    addShow() {
      this.editFlag = false;
      this.editData = {
                host: '',
                username: '',
                password: '',
                enable: 1,
                remark: ''
              }
      this.editShow = true;
    },
    editShowDialog(row) {
      this.editData = {
        ...row,
        // 编辑时不显示密码，留空表示不修改
        password: ''
      };
      this.editFlag = true;
      this.editShow = true;
    },
    closeShow() {
      this.editShow = false;
    },
    submit() {
      this.$refs.addRule.validate((valid) => {
        if (valid) {
          this.editLoading = true;
          if (this.editFlag) {
            // 编辑时，如果密码为空，则不包含在请求中
            if (this.editData.password === '') {
              delete this.editData.password;
            }
            putEditFeiniu(this.editData).then(res => {
              this.editLoading = false;
              this.$message({
                message: res.msg || '更新成功',
                type: 'success'
              });
              this.closeShow();
              this.getFeiniuList();
            }).catch(err => {
              this.editLoading = false;
              this.$message.error('更新失败');
            })
          } else {
            postAddFeiniu(this.editData).then(res => {
              this.editLoading = false;
              this.$message({
                message: res.msg || '新增成功',
                type: 'success'
              });
              this.closeShow();
              this.getFeiniuList();
            }).catch(err => {
              this.editLoading = false;
              this.$message.error('新增失败');
            })
          }
        }
      })
    },
    delFeiniu(feiniuId) {
      this.$confirm('操作不可逆，将永久删除该飞牛配置，仍要删除吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.deleteLoading = true;
        delFeiniu(feiniuId).then(res => {
          this.deleteLoading = false;
          this.$message({
            message: res.msg || '删除成功',
            type: 'success'
          });
          this.getFeiniuList();
        }).catch(err => {
          this.deleteLoading = false;
          this.$message.error('删除失败');
        })
      });
    },
    testConnection() {
      // 验证表单中的必填字段
      const validateFields = this.editFlag ? ['host', 'username'] : ['host', 'username', 'password'];
      this.$refs.addRule.validateField(validateFields, (valid) => {
        if (!valid) {
          this.testLoading = true;
          // 调用API测试连通性
          const testData = {
            host: this.editData.host,
            username: this.editData.username,
            password: this.editData.password,
            test: true
          };
          // 调用飞牛配置的POST接口测试连接
        testData.host = testData.host.replace(/\/$/, ''); // 去掉末尾的/，确保格式正确
          // 直接调用request，不使用postAddFeiniu，因为postAddFeiniu会将数据包装在feiniu对象中
          request({
            url: '/feiniu',
            headers: {
              isMask: false
            },
            method: 'post',
            data: testData
          }).then(res => {
            this.testLoading = false;
            if (res.data.success) {
              this.$message({
                message: res.data.message,
                type: 'success'
              });
            } else {
              this.$message({
                message: res.data.message,
                type: 'error'
              });
            }
        }).catch(err => {
          this.testLoading = false;
          this.$message({
            message: '测试连接失败：' + (err.message || '未知错误'),
            type: 'error'
          });
        });
      }
    });
    },
    testConnectionOnItem(item) {
      // 调用API测试连接
      this.testLoading = true;
      // 直接使用ID测试连接，后端会从数据库获取完整配置（包括密码）
      const testData = {
        id: item.id,
        test: true
      };
      // 调用飞牛配置的POST接口测试连接
      request({
        url: '/feiniu',
        headers: {
          isMask: false
        },
        method: 'post',
        data: testData
      }).then(res => {
        this.testLoading = false;
        if (res.data.success) {
          this.$message({
            message: res.data.message,
            type: 'success'
          });
        } else {
          this.$message({
            message: res.data.message,
            type: 'error'
          });
        }
      }).catch(err => {
        this.testLoading = false;
        this.$message({
          message: '测试连接失败：' + (err.message || '未知错误'),
          type: 'error'
        });
      });
    }
  }
}
</script>

<style lang="scss" scoped>
.feiniu-config {
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
}

@media (max-width: 480px) {
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

  ::v-deep .el-dialog {
    width: 95% !important;
    margin: 2.5vh auto !important;
  }

  .elform-box {
    padding: 16px;
    margin: 8px;
  }
}
</style>
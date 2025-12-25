import os
import compileall

# 检查所有Python文件的语法错误
compileall.compile_dir('.', force=True, quiet=True)
print("语法检查完成")
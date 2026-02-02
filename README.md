# OLED-Converter

一个用于转换江协科技旧版OLED代码到新版格式的Python GUI工具。

## 功能特点

- **两种转换模式**：
  - 模式1：直接将旧函数转换为新函数格式
  - 模式2：将所有函数转换为OLED_Printf格式
- **智能坐标转换**：自动将(行,列)坐标转换为(X,Y)像素坐标
- **支持所有OLED函数**：
  - OLED_ShowChar
  - OLED_ShowString
  - OLED_ShowNum
  - OLED_ShowSignedNum
  - OLED_ShowHexNum
  - OLED_ShowBinNum
- **可选的自动添加**：可选择在开头添加OLED_Clear()或在结尾添加OLED_Update()
- **友好的GUI界面**：无需命令行操作，图形化界面直观易用

## 安装要求

1. **Python 3.6+**
2. 需要安装的Python库：
   - tkinter（通常Python自带）

```bash
# 如果没有tkinter，可以通过以下方式安装
# Ubuntu/Debian:
sudo apt-get install python3-tk

# macOS:
brew install python-tk

# Windows: Python安装时通常已包含
```

## 使用方法

### 运行程序

```bash
python oled_converter.py
```

### 界面操作说明

1. **输入代码**：
   - 直接在左侧文本框粘贴您的旧版OLED代码
   - 点击"加载示例"查看示例代码
   - 点击"加载文件"从文件导入代码
   - 点击"清除"清空输入框

2. **转换设置**：
   - **转换模式**：
     - 模式1：保持原有函数结构，更新参数格式
     - 模式2：统一转换为OLED_Printf函数
   - **字体大小**：
     - OLED_8X16：8x16像素字体
     - OLED_6X8：6x8像素字体
   - **额外选项**：
     - 在开头添加OLED_Clear()
     - 在结尾添加OLED_Update()

3. **转换与输出**：
   - 点击"转换"按钮开始转换
   - 在右侧文本框查看转换结果
   - 使用"复制结果"复制到剪贴板
   - 使用"保存结果"保存到文件

## 支持的旧版函数格式

```c
// 旧版格式 (行,列) 坐标系统
OLED_ShowChar(1, 1, 'A');                    // 第1行第1列显示字符'A'
OLED_ShowString(1, 1, "Temperature: ");       // 显示字符串
OLED_ShowNum(2, 1, 1234, 4);                 // 显示数字，长度4
OLED_ShowSignedNum(3, 1, -567, 3);           // 显示有符号数字
OLED_ShowHexNum(4, 1, 0xABCD, 4);            // 显示十六进制数
OLED_ShowBinNum(4, 10, 0b1101, 4);           // 显示二进制数
```

## 转换示例

### 模式1转换结果
```c
// 转换前 (旧版)
OLED_ShowChar(1, 1, 'A');
OLED_ShowNum(2, 1, 1234, 4);

// 转换后 (新版)
OLED_ShowChar(0, 0, 'A', OLED_8X16);
OLED_ShowNum(0, 16, 1234, 4, OLED_8X16);
```

### 模式2转换结果
```c
// 转换前 (旧版)
OLED_ShowChar(1, 1, 'A');
OLED_ShowNum(2, 1, 1234, 4);

// 转换后 (OLED_Printf格式)
OLED_Printf(0, 0, OLED_8X16, "%c", 'A');
OLED_Printf(0, 16, OLED_8X16, "%4d", 1234);
```

## 坐标转换规则

- **旧版**：使用(行,列)系统，1行=16像素，1列=8像素
- **新版**：使用(X,Y)像素坐标系统
- **转换公式**：
  - X = (列 - 1) × 8
  - Y = (行 - 1) × 16

## 注意事项

1. **函数支持**：
   - OLED_ShowBinNum在模式2下会生成注释，因为OLED_Printf不支持二进制格式化
   - 需要在代码中手动实现二进制转换

2. **参数处理**：
   - 支持数字常量（如1, 2, 3）
   - 支持变量名（如line, column）
   - 支持表达式（如(x+1), (y*2)）

3. **代码格式**：
   - 保持原有注释
   - 保留代码缩进
   - 正确处理字符串中的逗号

4. **依赖关系**：
   - 确保目标工程已包含新版OLED驱动库
   - OLED_Printf函数需要相应的库支持

## 版本历史

- **v2.0** (当前版本)
  - 添加两种转换模式
  - 改进GUI界面
  - 支持更多OLED函数
  - 添加字体大小选项

- **v1.0** (初始版本)
  - 基础转换功能
  - 支持基本OLED函数

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

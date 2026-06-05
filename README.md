# 项目使用说明

## 项目简介

本项目是一个基于 Selenium 的自动学习脚本，主要用于：

- 读取本地 `config.json` 配置
- 自动打开内置浏览器并登录学习平台
- 进入指定课程链接并自动播放/推进课程
- 支持单链接或多链接课程处理
- 支持通过 PyInstaller 打包为单文件 `.exe` 进行一键执行

当前项目已经补齐了较新的 Selenium 兼容写法，并增加了自动打包脚本，可根据源码中的默认版本号自动生成对应名称的可执行文件。

---

## 目录说明

当前目录中几个关键文件的作用如下：

- `newLesson.py`

  - 主程序源码
  - 登录、课程推进、版本号读取等逻辑都在这里
- `config.json`

  - 运行配置文件
  - 包含账号、密码、课程链接等信息
- `build_newLesson.py`

  - Python 打包脚本
  - 会自动读取 `newLesson251031.py` 中 `self.version` 的默认值，并据此命名 exe
- `build_newLesson.bat`

  - Windows 一键打包入口
  - 双击即可执行打包流程
- `chromedriver.exe`

  - Chrome 驱动
  - 脚本运行和 exe 运行都依赖它
- `Application/`

  - 内置浏览器目录
  - 主程序默认会使用 `Application\chrome.exe`
- `newLesson-versionxxxxxx.exe`

  - 打包后的可执行文件
  - 文件名中的版本号来自源码默认版本值

---

## 运行原理

主程序启动后，大致流程如下：

1. 从 `config.json` 读取账号、密码、课程地址等配置
2. 启动本地 `chromedriver.exe`
3. 调起 `Application\chrome.exe`
4. 打开学习平台登录页并自动输入账号密码
5. 进入 `lessonUrl` 配置中的课程链接
6. 自动识别课程状态并进行播放、继续学习或跳转下一个课程

---

## 配置文件说明

配置文件为当前目录下的 `config.json`。

### 最小配置示例

```json
{
  "account": "你的账号",
  "password": "你的密码",
  "lessonUrl": [
    "课程链接1"
  ]
}
```

### 推荐配置示例

```json
{
  "account": "你的账号",
  "password": "你的密码",
  "lessonUrl": [
    "课程链接1",
    "课程链接2"
  ],
  "version": "20260605",
  "max_retry_count": 30,
  "chromedriver_port": 9515
}
```

### 字段说明

#### `account`

- 类型：字符串
- 说明：登录学习平台所使用的账号

#### `password`

- 类型：字符串
- 说明：登录学习平台所使用的密码

#### `lessonUrl`

- 类型：列表
- 说明：课程链接列表
- 支持一个或多个链接

示例：

```json
"lessonUrl": [
  "https://example.com/course1",
  "https://example.com/course2"
]
```

> 建议始终使用列表格式，即使只有 1 个链接，也写成列表，避免后续逻辑误判。

#### `version`

- 类型：字符串或数字
- 说明：运行时显示的软件版本号
- 如果配置文件中不写，程序会使用源码里的默认值

#### `max_retry_count`

- 类型：整数
- 默认值：`30`
- 说明：在课程跳转或重试过程中，允许的最大重试次数

#### `chromedriver_port`

- 类型：整数
- 默认值：`9515`
- 说明：启动 chromedriver 时使用的端口
- 一般不需要修改，只有端口冲突时才需要调整

---

## 如何调整配置

### 修改账号密码

直接编辑 `config.json`：

```json
{
  "account": "新账号",
  "password": "新密码",
  "lessonUrl": [
    "课程链接"
  ]
}
```

### 修改课程链接

将 `lessonUrl` 中的内容替换为实际课程地址即可：

```json
"lessonUrl": [
  "课程A链接",
  "课程B链接",
  "课程C链接"
]
```

### 调整版本号显示

有两种方式：

#### 方式一：只想影响本次运行显示

在 `config.json` 中添加或修改：

```json
"version": "v1"
```

这会影响程序运行时打印的版本号，但**不会改变打包输出文件名**。

#### 方式二：希望打包出的 exe 文件名也跟着变

修改源码 `newLesson.py` 中这一行的默认值：

```python
self.version = config.get('version', 20260605)
```

例如改成：

```python
self.version = config.get('version', 'v1')
```

那么打包时会自动生成：

```text
newLesson-versionv1.exe
```

> 打包脚本读取的是源码里的“默认值”，不是 `config.json` 里的 `version`。

### 调整重试次数

如果你希望课程跳转更保守或更激进，可以在 `config.json` 中加入：

```json
"max_retry_count": 50
```

### 调整 chromedriver 端口

如遇端口占用问题，可在 `config.json` 中增加：

```json
"chromedriver_port": 9516
```

---

## 如何运行源码

在当前目录打开终端后执行：

```bash
python newLesson.py
```

如果缺少依赖，通常需要安装：

```bash
python -m pip install selenium opencv-python
```

---

## 如何打包

### 方式一：双击一键打包

直接双击：

```text
build_newLesson.bat
```

它会自动调用：

```text
python build_newLesson.py
```

### 方式二：命令行打包

在当前目录执行：

```bash
python build_newLesson.py
```

### 打包脚本会做什么

`build_newLesson.py` 会自动完成以下工作：

1. 定位当前项目目录
2. 读取 `newLesson.py`
3. 解析这一行中的默认版本值：

```python
self.version = config.get('version', xxxxx)
```

4. 将版本号转换成合法文件名
5. 自动选择可用的 Python 解释器
6. 自动准备打包依赖：
   - `pyinstaller`
   - `selenium`
   - `opencv-python`
7. 运行 PyInstaller
8. 在当前目录输出：

```text
newLesson-version<版本号>.exe
```

例如：

```text
newLesson-versionxxxxx.exe
```

---

## 切换版本号时需要做什么

如果你只是想生成不同版本名的 exe，请按下面操作：

### 示例 1：改成日期版本

把源码中的：

```python
self.version = config.get('version', xxxxx)
```

改成：

```python
self.version = config.get('version', 20260630)
```

然后重新打包，输出文件将变为：

```text
newLesson-version20260630.exe
```

### 示例 2：改成字符串版本

把源码中的：

```python
self.version = config.get('version', xxxxx)
```

改成：

```python
self.version = config.get('version', 'v1')
```

然后重新打包，输出文件将变为：

```text
newLesson-versionv1.exe
```

---

## 如果以后替换打包脚本文件，需要做什么

这里分两种情况。

### 情况一：只是继续打包 `newLesson.py`

如果主程序文件名不变，通常只需要保留以下文件即可：

- `newLesson.py`
- `build_newLesson.py`
- `build_newLesson.bat`
- `config.json`
- `chromedriver.exe`
- `Application/`

这时不需要额外修改。

### 情况二：主程序文件名变了

例如你把主程序从：

```text
newLesson.py
```

换成：

```text
newLesson-new.py
```

那么需要同步修改 `build_newLesson.py` 顶部这一行：

```python
SCRIPT_NAME = "newLesson.py"
```

改成：

```python
SCRIPT_NAME = "newLesson-new.py"
```

如果你还想连 bat 文件名也同步，可以把：

- `build_newLesson.py`
- `build_newLesson.bat`

一起重命名，但这不是必须的。

### 情况三：你想换成另一个打包脚本

如果将来你想自己写新的打包脚本，至少需要保留以下几个核心能力：

1. 能定位主程序源码文件
2. 能解析 `self.version = config.get('version', 默认值)` 中的默认值
3. 能根据默认值生成 exe 文件名
4. 能调用 PyInstaller 进行打包
5. 能确保 `selenium`、`cv2` 等依赖在打包环境中可见

否则很容易出现：

- exe 文件名不跟版本号同步
- 打包能成功但运行时报缺模块
- 不同机器上使用了错误的 Python 解释器

---

## 打包产物说明

当前打包结果默认为：

```text
newLesson-version<默认版本>.exe
```

例如：

```text
newLesson-version20260605.exe
```

打包生成后，一般需要和以下资源放在同一目录下使用：

- `config.json`
- `chromedriver.exe`
- `Application/`

也就是说，exe 虽然是单文件，但它运行时仍依赖外部浏览器和驱动文件。

---

## 常见问题

### 1. 打包成功，但 exe 运行失败

优先检查以下内容：

- `chromedriver.exe` 是否存在
- `Application\chrome.exe` 是否存在
- `config.json` 是否放在 exe 同目录
- `config.json` 中账号密码和课程链接是否有效

### 2. 更改了 `config.json` 中的 `version`，为什么 exe 文件名没变

因为打包文件名读取的是源码默认值，不是配置文件中的运行时值。

如果你想让打包文件名改变，需要修改源码中的：

```python
self.version = config.get('version', ...)
```

里的默认值。

### 3. 只有一个课程链接，`lessonUrl` 能不能直接写字符串

不建议。

推荐始终写成列表：

```json
"lessonUrl": [
  "课程链接"
]
```

### 4. 打包脚本装依赖装到哪里

当前打包脚本会优先把打包相关依赖放到：

```text
build/pydeps/
```

这样做的好处是：

- 不容易污染你本机其他 Python 环境
- 更适合重复打包
- 更适合不同机器迁移

### 5. 打包中间文件在哪

主要在以下目录：

- `build/pydeps/`：本地打包依赖
- `build/pyinstaller/`：PyInstaller 工作目录
- `build/spec/`：生成的 spec 文件

---

## 建议的日常使用流程

### 修改课程配置时

1. 编辑 `config.json`
2. 直接运行源码或已有 exe

### 发布新版本 exe 时

1. 修改 `newLesson.py` 中 `self.version` 的默认值
2. 如有需要，修改业务逻辑
3. 双击 `build_newLesson.bat`
4. 检查生成的 exe 文件名是否符合预期
5. 将 exe、`config.json`、`chromedriver.exe`、`Application/` 一起保留或分发

---

## 安全提醒

- `config.json` 中包含明文账号密码，建议仅在个人可信设备上使用
- 如需分享项目，建议先清理或脱敏 `config.json`
- 不建议将真实账号密码直接提交到公开仓库

---

## 后续维护建议

如果未来页面结构变化、登录流程变化或课程按钮类名变化，优先排查：

- XPath 是否失效
- 页面 class 名是否变化
- 登录后是否出现新的弹窗或校验
- chromedriver 与浏览器版本是否兼容

如果未来切换到新的主程序文件名，只要同步调整打包脚本中的 `SCRIPT_NAME`，整套版本化打包流程仍然可以继续复用。

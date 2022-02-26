# 开发指南

## 准备软件

以下为需要安装的软件

- Git
- Python
- 一个Python IDE，例如PyCharm _（编辑代码）_
- Qt Creator *（编辑界面）*

## 准备环境


1. 在项目根目录下创建一个Python虚拟环境（可选）
2. 使用命令`pip install -r requirements.txt`补全依赖包。
3. 打开Qt Creator，点击`打开文件或项目`，打开项目根目录的项目文件`main.pyproj`

## 运行
1. 每次运行前，请在`Scripts`目录下运行脚本`Ready.bat`。这个脚本会将界面文件和资源文件使用PyQt的工具编译成Python文件。
2. 运行`warp.py`。

------
# 文件说明
## Scripts文件夹
本文件夹包含工具脚本。
### Ready.bat
将`.ui`文件转换为Python文件，并编译资源文件。
### Build.bat
将代码打包为`.exe`文件。

## UIFrames文件夹
本文件夹包含了实现各个界面的Python代码。其中以`ui`开头的文件（例如`ui_settings.py`）是实现界面的代码，需要通过运行上文的`Scripts.bat`生成。其它文件是实现界面功能的代码。

## function.py
后端功能代码。例如倒计时档案管理、配置文件管理功能。

## properties.py
存储了应用属性。里面包括了默认配置文件、应用信息。

## wcdapp.py
主程序。存储了应用程序类。

## warp.py
应用启动程序。这个应用会初始化运行环境并启动`wcdapp.py`中的应用程序类。


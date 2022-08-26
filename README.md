# TyJuliaCall

同元封装的Python调用Julia方案。

特性：

1. 提供Python-Julia环境同步功能。

    执行以下命令后，当前环境的Python和Julia环境正常链接，且解决PythonCall和PyCall冲突。

    ```bash
    python -c "import tyjuliacall"
    ```

2. 支持Python import语法导入任意Julia包

    ```python
    from tyjuliacall.Julia包名 import Julia函数或变量名
    ```

## 安装

1. 设置永久环境变量：

    ```bash
    JULIA_CONDAPKG_BACKEND=Null
    PYTHON_JULIAPKG_OFFLINE=yes
    JULIA_PYTHONCALL_EXE="@PyCall"
    ```

    特殊情况：如果使用映像，当映像**同时满足**以下条件时，应设置`JULIA_PYTHONCALL_EXE=<编译时使用的Python路径>`而不是 `@PyCall`:

    1. 从Julia启动映像
    2. 映像从Julia而非Python中生成
    3. 映像同时包含`PyCall`和`PythonCall`

2. 安装Python版本>=3.7，要求Python以动态链接方式编译，并预装matplotlib。

3. 安装`tyjuliacall`:

    ```bash
    cd <TyJuliaCall文件夹>
    pip install .
    ```

4. 安装Julia版本>=1.6，并先后预装PyCall和PythonCall包。


此外，对Julia用户，如果想要使用PythonCall前，应先导入PyCall。

## 映像加速

1. 使用当前环境中的Python和Julia创建映像 (需要在当前环境中安装 `tyjuliacall`)

    ```bash
    mk-ty-sysimage <Julia包1> <Julia包2> ... --out <映像输出路径> --python <可选：使用的Python解释器路径，默认为当前Python>

    # 打包PyCall, PythonCall, TySignalProcessing, DataFrames, 输出到'a.dll'，使用python解释器'xxx/python.exe'
    mk-ty-sysimage PyCall PythonCall TySignalProcessing DataFrames --out a.dll --python xxx/python.exe
    ```

    注意：如果用`--python`指定Python环境，则该python需要已安装`tyjuliacall`。**如果该环境是conda环境，则需要预先开启相应的conda环境。**

    如果需要使用Syslab自带的Python制作映像，建议使用Syslab配置环境，流程如下：

    1. 在Syslab中选择Python解释器，激活环境。如果Syslab切换/激活Python环境失败，尝试启动VSCode进行相同操作。

    2. 激活Python环境后，在Syslab/VSCode终端中使用`mk-ty-sysimage`命令。

使用映像：Python用户设置`TYPY_JL_SYSIMAGE`为映像路径，且设置`TYPY_NOSETUP=true`, 并`import tyjuliacall`。


## 受信赖的数据转换规则 (TODO)

JuliaPython:

| Julia        | Python    |
|:------------:|:---------:|
| `nothing`    | `None`    |
| `missing`    | `None`
| `Int`        | `int`     |
| `Bool`       | `bool`    |


## Troubleshooting

1. 导入`tyjuliacall`时，报错 `ERROR: InitError: AssertionError: pystr_asstring(jl.__version__) == string(VERSION)`。

    解决：删除`$JULIA_DEPOT_PATH\packages\PythonCall`文件夹，并在Julia中重装PythonCall。


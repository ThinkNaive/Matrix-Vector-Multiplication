# *Matrix Vector Multiplication*

## 实验方法
&emsp;&emsp;数据生成详见`analyses/ParamGen.py`和`analyses/ScaleGen.py`；

&emsp;&emsp;数据分析详见`analyses/ParamAnalyzer.py`、`analyses/ScaleAnalyzer.py`和`analyses/RSAnalyzer.py`。

## 测试方法

&emsp;&emsp;为python指定根目录为工作目录。

&emsp;&emsp;打开若干个命令行窗口，master一个，slave一个，分别在窗口调用`python master.py`和`python slave.py`。

&emsp;&emsp;&emsp;&emsp;在`connection.py`中修改`verbose`，`HOST`，`PORT`；

&emsp;&emsp;&emsp;&emsp;在`slave.py`中修改`params`；

&emsp;&emsp;&emsp;&emsp;在`master.py`中修改`row`、`col`、`iteration`、`index`、`params`。

## 主节点代码含义（*master.py*）

&emsp;&emsp;`results = Handler.run(host, port, data)`将建立对端口的监听，并对输入数据分片，交由工作节点计算，当所有计算任务完成时，此方法收集计算结果并返回。

## 工作节点代码含义（*slave.py*）

### 步骤1
&emsp;&emsp;`handle = Handler(host, port)`将建立一个新实例。
### 步骤2
&emsp;&emsp;`handle.compute()`询问是否可计算
### 步骤3
&emsp;&emsp;`handle.pull()`接收主节点数据，若返回`None`则表明主节点拒绝为其分配计算任务。
### 步骤4
&emsp;&emsp;`handle.push(data)`向主节点发送数据，此方法将持续至数据发送完成。

## 下一步计划

- [x] LT性能分析工具优化

- [x] 分离主节点数据收发端口

- [x] 方法性能分析——参数对比实验

- [x] 方法性能分析——规模对比实验

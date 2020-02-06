# Matrix-Vector-Multiplication
~~现在master.py和slave.py仅有**基础**的通信功能~~

现在rep策略的实现已完成

## 测试方法
&emsp;打开若干个命令行窗口，master一个，~~slave一个，分别在窗口调用`python master-xx.py`和`python slave.py`

## 主节点代码含义（master-xx.py）

&emsp;`results = Handler.run(host, port, data)`将建立对端口的监听，并对输入数据分片，交由工作节点计算，当所有计算任务完成时，此方法收集计算结果并返回

## 工作节点代码含义（slave.py）

### 步骤1
&emsp;`handle = Handler(host, port)`将建立一个新实例
### 步骤2
&emsp;`handle.poll()`接收主节点数据，若返回`None`则表明主节点拒绝为其分配计算任务
### 步骤3
&emsp;`handle.push(data)`向主节点发送数据，此方法将持续至数据发送完成

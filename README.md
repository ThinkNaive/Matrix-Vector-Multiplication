# Matrix-Vector-Multiplication
现在master.py和slave.py仅有**最基础**的通信（小于1024字节）功能

## 主节点调用格式（master.py）

### 步骤1
&emsp;`Handler.run(host, port, data)`将建立对端口的监听，并对输入数据分片，交由工作节点计算，当所有计算任务完成时，此方法收集计算结果并返回
### 步骤2
&emsp;`Handler.outputList`返回各工作节点的计算结果

## 工作节点调用格式（slave.py）

### 步骤1
&emsp;`handle = Handler(host, port)`将建立一个新实例
### 步骤2
&emsp;`handle.poll()`接收主节点数据，若返回`None`则表明主节点拒绝为其分配计算任务
### 步骤3
&emsp;`handle.push(data)`向主节点发送数据，此方法将持续至数据发送完成

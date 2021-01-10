# jenkins-exporter
作为 prometheus 的客户端，用于获取 Jenkins 中处于构建中的 build, 以及获取每个 build 信息，目的是在 grafana 中动态展示 jenkins 正在构建的项目、构建耗时、由谁触发的构建、最近的构建历史。  

项目中使用 python-jenkins 这个 jenkins python api 来获取 job 和 build 信息; 使用 jenkins 的 rss 获取最近的构建历史;

## Metrics 具体如下：
### 1. jenkins_job_build_duration :  每个 build 构建耗时, label 如下：
1. job_name: 构建的 job 名称
2. build_number: 构建的序号
3. building: 是否处于正在构建过程中
4. node: 实际构建的节点, 由于使用 jenkins cloud 模式, 实际执行构建的节点是 k8s 中的动态 pod
5. result: 构建结果
6. start_time: 构建的开始时间
7. user: 触发构建的用户, 是这个项目的最原始需求
8. url: 构建的 url

### 2. jenkins_job_build_result : 每个 build 的构建结果, 实际 label 在上面的基础上新增如下。因为 PromQL 不支持基于 label 值进行排序和比较，所以额外新增这个 metric
1. in_3hours: 是否是 3 小时内的构建, 便于在 grafana 中展示 3 小时内构建历史
   
### 3. jenkins_job_building : 获取正在进行构建的 job, labels 同上
  
    
# 运行方式
## 本地测试
1. 在项目目录下，执行如下命令
`python main.py --url="<jenkins 地址>" --user="<jenkins 用户名>" --password="<jenkins 密码或 token>`
2. 本地访问 `curl http://127.0.0.1:8888/metrics` 进行测试
## 实际部署
1. 根据目录中的 Dockerfile 制作镜像
2. 通过 k8s 运行该镜像, 需要修改项目目录中的 jenkins-exporter.yml; 这里使用了 nodeport 方式暴露了 jenkins-exporter pod 的连接地址给 k8s 外部的 prometheus
3. 在接入 prometheus 测试没问题后，将项目目录中的 ** Jenkins 构建大盘-1610271187373.json ** 导入到 grafana 中

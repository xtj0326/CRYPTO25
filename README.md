# 混沌映射加密/解密系统

本仓库内容为中科大2025春密码学导论课程实践作品题。实现了基于混沌系统的文本和图像加密解密工具，采用Logistic、Chebyshev和Tent三种混沌映射生成置乱序列。

## 项目结构

- **chaotic_permutation.py**: 核心库文件，实现三种混沌映射、置乱序列生成及可视化
- **analysis.py**: 分析工具，用于研究置乱表生成时间与平均阶-N的关系
- **gui.py**: 图形用户界面，提供文本和图像的加密解密功能
- **REPORT.pdf**：实验报告

## 快速开始

1. 安装依赖：`pip install numpy matplotlib pillow tkinterdnd2`
2. 启动图形界面：`python gui.py`
3. 运行性能分析：`python analysis.py`
4. 查看置乱效果：`python chaotic_permutation.py`

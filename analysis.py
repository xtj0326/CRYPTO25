import numpy as np
import matplotlib.pyplot as plt
from chaotic_permutation import generate_permutation, logistic_map, chebyshev_map, tent_map
import time
import random
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

# 计算最小公倍数
def lcm(lst):
    if len(lst) == 0:
        return 1
    lcm = lst[0]
    for i in range(1, len(lst)):
        lcm = np.lcm(lcm, lst[i])
    return lcm

def calc_order(perm):
    visited = set()
    order = []

    # 寻找所有循环并记录长度
    for i, val in enumerate(perm):
        if i not in visited:
            cycle_length = 0
            j = i
            while j not in visited:
                visited.add(j)
                j = perm[j]
                cycle_length += 1
            order.append(cycle_length)

    # 返回所有循环长度的最小公倍数
    return lcm(order) if order else 1

# 平均阶和生成时间
def avg_order(chaotic_map, n_size, num_seeds=30, map_params=None):
    if map_params is None:
        map_params = {}
    
    orders = []
    times = []
    
    for _ in range(num_seeds):
        seed = random.uniform(0.1, 0.9)
        start_time = time.time()
        perm = generate_permutation(chaotic_map, seed, n_size, transient=1000, **map_params)
        end_time = time.time()
        gen_time = end_time - start_time
        order = calc_order(perm)
        orders.append(order)
        times.append(gen_time)
    
    avg_order = np.mean(orders)
    avg_time = np.mean(times)
    return avg_order, orders, avg_time

def test_sizes(chaotic_map, map_name, map_params=None, min_size=10, max_size=200, step=10, num_seeds=30):
    if map_params is None:
        map_params = {}
    
    sizes = list(range(min_size, max_size + 1, step))
    orders = []
    times = []
    
    total_steps = len(sizes)
    
    # 平均阶和时间
    for i, size in enumerate(sizes):
        avg_ord, all_orders, avg_time = avg_order(chaotic_map, size, num_seeds, map_params)
        orders.append(avg_ord)
        times.append(avg_time)
        print(f"处理进度: {i+1}/{total_steps}")
    
    return sizes, orders, times

# 绘制分析结果
def plot_results(chaotic_maps, map_names, map_params_list, min_size=10, max_size=200, step=10, num_seeds=30):
    plt.figure(figsize=(12, 8))
    
    all_sizes = []
    all_orders = []
    all_times = []
    
    for chaotic_map, map_name, map_params in zip(chaotic_maps, map_names, map_params_list):
        print(f"\n分析 {map_name} 映射...")
        sizes, orders, times = test_sizes(
            chaotic_map, map_name, map_params, min_size, max_size, step, num_seeds
        )
        
        all_sizes.append(sizes)
        all_orders.append(orders)
        all_times.append(times)
        
        # 将阶转换为分贝单位
        orders_db = [20 * np.log10(order) if order > 0 else 0 for order in orders]
        plt.plot(sizes, orders_db, marker='o', label=f"{map_name}映射")
    
    for sizes, orders, map_name in zip(all_sizes, all_orders, map_names):
        orders_db = [20 * np.log10(order) if order > 0 else 0 for order in orders]
        z = np.polyfit(sizes, orders_db, 5)
        p = np.poly1d(z)
        x_trend = np.linspace(min(sizes), max(sizes), 500)
        plt.plot(x_trend, p(x_trend), '--', label=f"{map_name}拟合曲线")
    
    plt.title(f"不同混沌映射的置乱表平均阶与大小N的关系 (每个N使用{num_seeds}个不同种子)")
    plt.xlabel("置乱表大小 (N)")
    plt.ylabel("平均阶 (dB)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    folder_path = f"./plot/test_count={num_seeds}_in_{min_size}to{max_size}"
    os.makedirs(folder_path, exist_ok=True)
    
    filename = f"{folder_path}/order_ave_vs_N.png"
    plt.savefig(filename, dpi=300)
    print(f"\n阶分析结果已保存为 '{filename}'")
    
    plot_times(all_sizes, all_times, map_names, min_size, max_size, step, num_seeds, folder_path)
    
    plt.show()

def plot_times(all_sizes, all_times, map_names, min_size, max_size, step, num_seeds, folder_path):
    plt.figure(figsize=(12, 8))
    
    for sizes, times, map_name in zip(all_sizes, all_times, map_names):
        times_ms = [t * 1000 for t in times]
        plt.plot(sizes, times_ms, marker='o', label=f"{map_name}映射")
    
    for sizes, times, map_name in zip(all_sizes, all_times, map_names):
        times_ms = [t * 1000 for t in times]
        z = np.polyfit(sizes, times_ms, 3)
        p = np.poly1d(z)
        x_trend = np.linspace(min(sizes), max(sizes), 500)
        plt.plot(x_trend, p(x_trend), '--', label=f"{map_name}拟合曲线")
    
    plt.title(f"不同混沌映射的置乱表生成时间与大小N的关系 (每个N使用{num_seeds}个不同种子)")
    plt.xlabel("置乱表大小 (N)")
    plt.ylabel("平均生成时间 (毫秒)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    filename = f"{folder_path}/time_ave_vs_N.png"
    plt.savefig(filename, dpi=300)
    print(f"置乱表生成时间分析结果已保存为 '{filename}'")

def main():
    chaotic_maps = [logistic_map, chebyshev_map, tent_map]
    map_names = ["Logistic", "Chebyshev", "Tent"]
    map_params_list = [
        {"mu": 3.99},
        {"n": 3},
        {"mu": 1.99}
    ]
    
    min_size = 50    
    max_size = 1000  
    step = 50        
    num_seeds = 100  
    
    print(f"开始分析置乱表平均阶与大小N的关系...")
    print(f"参数设置: N范围={min_size}-{max_size}, 步长={step}, 每个N使用{num_seeds}个不同种子")
    
    plot_results(chaotic_maps, map_names, map_params_list, min_size, max_size, step, num_seeds)

if __name__ == "__main__":
    main() 

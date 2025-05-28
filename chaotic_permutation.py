import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.font_manager as f

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

def logistic_map(x, mu=3.99):
    """当μ=3.99时,系统表现出混沌特性"""
    return mu * x * (1 - x)

def chebyshev_map(x, n=3):
    return np.cos(n * np.arccos(x))

def tent_map(x, mu=1.99):
    """当μ接近2时,系统表现出混沌特性"""
    return mu * np.minimum(x, 1 - x)

def generate_permutation(chaotic_map, seed, size, transient=1000, **params):
    """使用混沌映射生成置乱序列"""
    x = seed
    
    for _ in range(transient):
        x = chaotic_map(x, **params)
    
    sequence = [x]
    for _ in range(size - 1):
        x = chaotic_map(x, **params)
        sequence.append(x)
    
    sorted_sequence = sorted(sequence)
    permutation = []
    for value in sequence:
        permutation.append(sorted_sequence.index(value))
    
    return permutation

def analyze_cycles(permutation):
    """分析置乱序列的循环结构"""
    visited = set()
    cycle_lengths = []

    for i, val in enumerate(permutation):
        if i not in visited:
            cycle_length = 0
            j = i
            while j not in visited:
                visited.add(j)
                j = permutation[j]
                cycle_length += 1
            cycle_lengths.append(cycle_length)

    cycle_counts = Counter(cycle_lengths)
    
    def lcm_of_list(lst):
        if len(lst) == 0:
            return 1
        lcm = lst[0]
        for i in range(1, len(lst)):
            lcm = np.lcm(lcm, lst[i])
        return lcm
    
    total_order = lcm_of_list(cycle_lengths)
    
    return cycle_counts, total_order

def print_cycle_analysis(name, cycle_counts, total_order, permutation_size):
    print(f"\n{name} 映射分析 (置乱序列大小: {permutation_size})")
    print("-" * 50)
    print("循环结构:")
    total_cycles = sum(cycle_counts.values())
    for length, count in sorted(cycle_counts.items()):
        print(f"  {count} 个长度为 {length} 的循环")
    print(f"循环总数: {total_cycles}")
    print(f"总阶(循环长度的最小公倍数): {total_order}")
    print("-" * 50)

def main():
    size = 500
    seed = 0.1
    
    logistic_perm = generate_permutation(
        logistic_map, seed, size, mu=3.99
    )
    logistic_cycles, logistic_order = analyze_cycles(logistic_perm)
    print_cycle_analysis("Logistic", logistic_cycles, logistic_order, size)

    chebyshev_perm = generate_permutation(
        chebyshev_map, seed, size, n=3
    )
    chebyshev_cycles, chebyshev_order = analyze_cycles(chebyshev_perm)
    print_cycle_analysis("Chebyshev", chebyshev_cycles, chebyshev_order, size)
    
    tent_perm = generate_permutation(
        tent_map, seed, size, mu=1.99
    )
    tent_cycles, tent_order = analyze_cycles(tent_perm)
    print_cycle_analysis("Tent", tent_cycles, tent_order, size)
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.scatter(range(size), logistic_perm, s=10)
    plt.title("Logistic映射置乱")
    plt.xlabel("原始位置")
    plt.ylabel("新位置")
    
    plt.subplot(1, 3, 2)
    plt.scatter(range(size), chebyshev_perm, s=10)
    plt.title("Chebyshev映射置乱")
    plt.xlabel("原始位置")
    plt.ylabel("新位置")
    
    plt.subplot(1, 3, 3)
    plt.scatter(range(size), tent_perm, s=10)
    plt.title("帐篷映射置乱")
    plt.xlabel("原始位置")
    plt.ylabel("新位置")
    
    plt.tight_layout()
    plt.savefig("chaotic_permutations.png", dpi=300)
    plt.close()
    
    print("\n置乱结果可视化已保存为 'chaotic_permutations.png'")

if __name__ == "__main__":
    main() 

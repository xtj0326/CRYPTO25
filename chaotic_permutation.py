import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

def logistic_map(x, mu=3.99):
    return mu * x * (1 - x)

def chebyshev_map(x, n=3):
    return np.cos(n * np.arccos(x))

def tent_map(x, mu=1.99):
    return mu * np.minimum(x, 1 - x)

def generate_permutation(chaotic_map, seed, size, transient=1000, **params):
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

def main():
    size = 500
    seed = 0.1
    
    logistic_perm = generate_permutation(
        logistic_map, seed, size, mu=3.99
    )
    
    chebyshev_perm = generate_permutation(
        chebyshev_map, seed, size, n=3
    )
    
    tent_perm = generate_permutation(
        tent_map, seed, size, mu=1.99
    )
    
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

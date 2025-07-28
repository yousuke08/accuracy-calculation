from scripts.components import Component
import matplotlib.pyplot as plt

# コンポーネントの作成
resistor = Component(typ_value=1000, random_tolerance=5, temp_coefficient=100, seed=42)

# 誤差分布の可視化 (50℃での分布)
resistor.visualize_error_distribution(50)

# 図をJPEG形式で保存
plt.savefig('error_distribution.jpg', format='jpg', dpi=300, bbox_inches='tight')
print("誤差分布の図が 'error_distribution.jpg' として保存されました。")
from scripts.components import Component
import matplotlib.pyplot as plt

# コンポーネントの作成
resistor = Component(typ_value=1000, room_temp_tolerance=(-2, 3), temp_coefficient=100, max_temp_tolerance=(-5, 5), max_operating_temperature=85, sigma=4.5, seed=42)

# 誤差分布の可視化 (50℃での分布)
resistor.visualize_error_distribution()

# 図をJPEG形式で保存
plt.savefig('error_distribution.jpg', format='jpg', dpi=300, bbox_inches='tight')
print("誤差分布の図が 'error_distribution.jpg' として保存されました。")


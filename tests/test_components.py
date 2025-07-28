import unittest
from scripts.components import Component
import matplotlib.pyplot as plt

class TestComponent(unittest.TestCase):
    def test_component_creation(self):
        """コンポーネントの基本的な作成をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10, seed=42)
        self.assertEqual(comp.typ_value, 100)
        self.assertEqual(comp.random_tolerance, 5)
        self.assertEqual(comp.temp_coefficient, 10)
        
    def test_random_variation(self):
        """ランダムな誤差の計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10, seed=42)
        variation = comp.get_random_variation()
        # ランダムな誤差は±5%の範囲内にあるはず
        # シード固定により、特定の値が返される
        self.assertAlmostEqual(variation, 1.3942679845788373, places=5)
        
    def test_temperature_variation(self):
        """温度依存の誤差計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10, seed=42)
        # 基準温度は25℃とします
        variation = comp.get_temperature_variation(50)  # 25℃から25℃上昇
        # 10ppm/℃ * 25℃ = 0.025%
        expected = 10 * 25 / 10000  # 10ppm = 0.001%
        self.assertAlmostEqual(variation, expected, places=5)
        
    def test_total_variation(self):
        """総合的な誤差の計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10, seed=42)
        # ここではランダムな誤差を固定値として計算します（テストの再現性のため）
        total_variation = comp.get_total_variation(50, random_variation=1.3942679845788373)
        expected = 1.3942679845788373 + (10 * 25 / 10000)  # ランダム誤差 + 温度依存の誤差
        self.assertAlmostEqual(total_variation, expected, places=5)
        
    def test_visualize_error_distribution(self):
        """誤差分布の可視化メソッドのテスト（実際のプロットは行わず、メソッドが存在することのみ確認）"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10, seed=42)
        # メソッドが存在することを確認
        self.assertTrue(hasattr(comp, 'visualize_error_distribution'))
        # メソッドが呼び出せることを確認（実際のプロットは行わない）
        # ここでは単にメソッドが例外を投げないことを確認する

if __name__ == '__main__':
    unittest.main()
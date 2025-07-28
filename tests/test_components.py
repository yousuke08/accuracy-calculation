import unittest
from scripts.components import Component

class TestComponent(unittest.TestCase):
    def test_component_creation(self):
        """コンポーネントの基本的な作成をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10)
        self.assertEqual(comp.typ_value, 100)
        self.assertEqual(comp.random_tolerance, 5)
        self.assertEqual(comp.temp_coefficient, 10)
        
    def test_random_variation(self):
        """ランダムな誤差の計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10)
        variation = comp.get_random_variation()
        # ランダムな誤差は±5%の範囲内にあるはず
        self.assertTrue(-5 <= variation <= 5)
        
    def test_temperature_variation(self):
        """温度依存の誤差計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10)
        # 基準温度は25℃とします
        variation = comp.get_temperature_variation(50)  # 25℃から25℃上昇
        # 10ppm/℃ * 25℃ = 0.025%
        expected = 10 * 25 / 10000  # 10ppm = 0.001%
        self.assertAlmostEqual(variation, expected, places=5)
        
    def test_total_variation(self):
        """総合的な誤差の計算をテスト"""
        comp = Component(typ_value=100, random_tolerance=5, temp_coefficient=10)
        # ここではランダムな誤差を0として計算します（テストの再現性のため）
        total_variation = comp.get_total_variation(50, random_variation=0)
        expected = 10 * 25 / 10000  # 温度依存の誤差のみ
        self.assertAlmostEqual(total_variation, expected, places=5)

if __name__ == '__main__':
    unittest.main()
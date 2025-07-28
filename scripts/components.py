import random
import matplotlib.pyplot as plt
import numpy as np

class Component:
    """電子回路の要素を表すクラス"""
    
    def __init__(self, typ_value, random_tolerance, temp_coefficient, seed=None):
        """
        コンポーネントの初期化
        
        Args:
            typ_value (float): 典型値
            random_tolerance (float): ランダムな誤差（％）
            temp_coefficient (float): 温度係数（ppm/℃）
            seed (int, optional): ランダムジェネレータのシード
        """
        self.typ_value = typ_value
        self.random_tolerance = random_tolerance
        self.temp_coefficient = temp_coefficient
        # ランダムジェネレータの作成
        self.random_generator = random.Random(seed)
        
    def get_random_variation(self):
        """
        ランダムな誤差を取得する
        
        Returns:
            float: ランダムな誤差（％）
        """
        return self.random_generator.uniform(-self.random_tolerance, self.random_tolerance)
        
    def get_temperature_variation(self, temperature):
        """
        温度依存の誤差を計算する
        
        Args:
            temperature (float): 現在の温度（℃）
            
        Returns:
            float: 温度依存の誤差（％）
        """
        # 基準温度は25℃とする
        reference_temp = 25
        temp_diff = temperature - reference_temp
        # ppmを%に変換 (1ppm = 0.0001%)
        return self.temp_coefficient * temp_diff / 10000
        
    def get_total_variation(self, temperature, random_variation=None):
        """
        総合的な誤差を計算する
        
        Args:
            temperature (float): 現在の温度（℃）
            random_variation (float, optional): ランダムな誤差（％）。指定しない場合はランダムに生成される
            
        Returns:
            float: 総合的な誤差（％）
        """
        if random_variation is None:
            random_variation = self.get_random_variation()
        temp_variation = self.get_temperature_variation(temperature)
        return random_variation + temp_variation
        
    def visualize_error_distribution(self, temperature, sample_size=10000):
        """
        誤差分布を可視化する
        
        Args:
            temperature (float): 温度（℃）
            sample_size (int): サンプル数（デフォルト: 10000）
        """
        # ランダム誤差のサンプルを生成
        random_errors = [self.get_random_variation() for _ in range(sample_size)]
        
        # 温度誤差を計算
        temp_error = self.get_temperature_variation(temperature)
        
        # 総合誤差を計算
        total_errors = [random_error + temp_error for random_error in random_errors]
        
        # ヒストグラムをプロット
        plt.figure(figsize=(10, 6))
        
        # ランダム誤差の分布
        plt.subplot(1, 2, 1)
        plt.hist(random_errors, bins=50, alpha=0.7, color='blue', edgecolor='black')
        plt.title('Random Error Distribution')
        plt.xlabel('Error (%)')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        # 総合誤差の分布
        plt.subplot(1, 2, 2)
        plt.hist(total_errors, bins=50, alpha=0.7, color='green', edgecolor='black')
        plt.title('Total Error Distribution')
        plt.xlabel('Error (%)')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
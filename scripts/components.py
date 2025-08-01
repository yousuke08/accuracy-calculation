import random
import matplotlib.pyplot as plt
import numpy as np

class Component:
    """電子回路の要素を表すクラス"""
    
    def __init__(self, typ_value, room_temp_tolerance, temp_coefficient, max_temp_tolerance=None, max_operating_temperature=None, sigma=None, seed=None):
        """
        コンポーネントの初期化
        
        Args:
            typ_value (float): 典型値
            room_temp_tolerance (float or tuple): 常温におけるランダムな誤差（％）。単一の数値の場合は±その値の範囲、タプルの場合は(min_tolerance, max_tolerance)の範囲。
            temp_coefficient (float): 温度係数（ppm/℃）
            max_temp_tolerance (float or tuple, optional): 最大動作温度におけるランダムな誤差（％）。指定しない場合はroom_temp_toleranceが使用されます。
            max_operating_temperature (float, optional): 最大動作温度（℃）。max_temp_toleranceが指定された場合に必要です。
            sigma (float, optional): ランダム誤差の分布のシグマ値。指定しない場合は4.5をデフォルトとします。
            seed (int, optional): ランダムジェネレータのシード
        """
        self.typ_value = typ_value
        self.room_temp_tolerance = room_temp_tolerance
        self.temp_coefficient = temp_coefficient
        self.max_temp_tolerance = max_temp_tolerance
        self.max_operating_temperature = max_operating_temperature
        self.sigma = sigma if sigma is not None else 4.5 # デフォルト値を4.5に設定
            
        # ランダムジェネレータの作成
        self.random_generator = random.Random(seed)

    def _calculate_random_variation(self, tolerance_range):
        """
        指定された許容範囲に基づいてランダムな誤差を計算するヘルパーメソッド
        """
        if isinstance(tolerance_range, (tuple, list)) and len(tolerance_range) == 2:
            min_val = tolerance_range[0]
            max_val = tolerance_range[1]
        else:
            min_val = -abs(tolerance_range)
            max_val = abs(tolerance_range)

        mean = (min_val + max_val) / 2
        std_dev = (max_val - min_val) / (2 * self.sigma)
        return self.random_generator.gauss(mean, std_dev)
        
    def get_random_variation(self, temperature):
        """
        ランダムな誤差を取得する。温度に応じて適切なばらつき範囲を使用する。
        
        Args:
            temperature (float): 現在の温度（℃）
            
        Returns:
            float: ランダムな誤差（％）
        """
        if self.max_temp_tolerance is not None and self.max_operating_temperature is not None and temperature == self.max_operating_temperature:
            return self._calculate_random_variation(self.max_temp_tolerance)
        else:
            return self._calculate_random_variation(self.room_temp_tolerance)
        
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
            random_variation = self.get_random_variation(temperature)
        temp_variation = self.get_temperature_variation(temperature)
        return random_variation + temp_variation
        
    def visualize_error_distribution(self, sample_size=10000):
        """
        誤差分布を可視化する
        
        Args:
            temperature (float): 温度（℃）
            sample_size (int): サンプル数（デフォルト: 10000）
        """
        # 基準温度は25℃とする
        reference_temp = 25

        # 室温における誤差のサンプルを生成
        random_errors_room_temp = [self.get_random_variation(reference_temp) for _ in range(sample_size)]
        temp_error_room_temp = self.get_temperature_variation(reference_temp)
        total_errors_room_temp = [random_error + temp_error_room_temp for random_error in random_errors_room_temp]

        # 最大動作温度における誤差のサンプルを生成
        if self.max_operating_temperature is not None:
            random_errors_max_temp = [self.get_random_variation(self.max_operating_temperature) for _ in range(sample_size)]
            temp_error_max_temp = self.get_temperature_variation(self.max_operating_temperature)
            total_errors_max_temp = [random_error + temp_error_max_temp for random_error in random_errors_max_temp]
        else:
            total_errors_max_temp = [] # 最大動作温度が設定されていない場合は空リスト

        # ヒストグラムをプロット
        plt.figure(figsize=(10, 6))
        
        # 総合誤差の分布を重ねて表示
        plt.hist(total_errors_room_temp, bins=50, alpha=0.7, color='blue', edgecolor='black', label=f'Room Temp ({reference_temp}°C) Total Error')
        if total_errors_max_temp:
            plt.hist(total_errors_max_temp, bins=50, alpha=0.7, color='red', edgecolor='black', label=f'Max Temp ({self.max_operating_temperature}°C) Total Error')
        
        plt.title('Total Error Distribution at Different Temperatures')
        plt.xlabel('Error (%)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True)
        
        
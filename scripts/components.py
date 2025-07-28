import random

class Component:
    """電子回路の要素を表すクラス"""
    
    def __init__(self, typ_value, random_tolerance, temp_coefficient):
        """
        コンポーネントの初期化
        
        Args:
            typ_value (float): 典型値
            random_tolerance (float): ランダムな誤差（％）
            temp_coefficient (float): 温度係数（ppm/℃）
        """
        self.typ_value = typ_value
        self.random_tolerance = random_tolerance
        self.temp_coefficient = temp_coefficient
        
    def get_random_variation(self):
        """
        ランダムな誤差を取得する
        
        Returns:
            float: ランダムな誤差（％）
        """
        return random.uniform(-self.random_tolerance, self.random_tolerance)
        
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
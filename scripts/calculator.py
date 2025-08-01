from scripts.components import Component

class Calculator:
    """
    回路の誤差計算を行うクラス。
    複数のコンポーネントインスタンスを管理し、合成誤差の計算を行う。
    """
    def __init__(self, component_params_list):
        """
        Calculatorクラスの初期化。
        指定されたパラメータリストに基づいてComponentインスタンスを生成し、管理する。

        Args:
            component_params_list (list): 各コンポーネントのパラメータを含む辞書のリスト。
                                          各辞書はComponentクラスの__init__に渡される引数に対応する。
                                          必須キー: 'symbol', 'typ_value', 'room_temp_tolerance', 'temp_coefficient'
                                          オプションキー: 'max_temp_tolerance', 'max_operating_temperature', 'sigma', 'seed'
        """
        self.components = {}
        for params in component_params_list:
            symbol = params.pop('symbol') # シンボル名を抽出し、残りをComponentの引数として渡す
            self.components[symbol] = Component(**params)
            
    def get_component(self, symbol):
        """
        指定されたシンボル名のComponentインスタンスを取得する。
        """
        return self.components.get(symbol)

    # 今後、合成誤差計算のためのメソッドをここに追加していく

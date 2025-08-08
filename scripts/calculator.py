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
            symbol = params.pop('symbol')
            # typ_valueはComponentの__init__に渡される
            self.components[symbol] = Component(**params)
            
    def get_component(self, symbol):
        """
        指定されたシンボル名のComponentインスタンスを取得する。
        """
        return self.components.get(symbol)

    def get_actual_component_value(self, symbol, temperature):
        """
        指定されたシンボルのコンポーネントの、ばらつきを考慮した実際の値を取得する。
        
        Args:
            symbol (str): コンポーネントのシンボル名。
            temperature (float): 現在の温度（℃）。
            
        Returns:
            float: ばらつきを考慮したコンポーネントの実際の値。
        """
        component = self.get_component(symbol)
        if not component:
            raise ValueError(f"Component with symbol {symbol} not found.")

        # 汎用Componentの場合、typ_valueに誤差を適用
        total_variation = component.get_total_variation(temperature)
        return component.typ_value * (1 + total_variation / 100)

    def evaluate_formula(self, formula_func, component_symbols, input_params, temperature):
        """
        指定された計算式を、現在のコンポーネントのばらつきと入力パラメータで評価する。

        Args:
            formula_func (callable): 計算式を表す関数。引数として(component_values, input_params)を受け取る。
                                     component_valuesは{symbol: actual_value}の辞書。
                                     input_paramsはその他の入力パラメータの辞書。
            component_symbols (list): 計算式で使用するコンポーネントのシンボル名のリスト。
            input_params (dict): 計算式に渡すその他の入力パラメータの辞書。
            temperature (float): 現在の温度（℃）。

        Returns:
            float: 計算式の評価結果。
        """
        actual_component_values = {}
        for symbol in component_symbols:
            actual_component_values[symbol] = self.get_actual_component_value(symbol, temperature)

        return formula_func(actual_component_values, input_params)

    # 今後、合成誤差計算のためのメソッドをここに追加していく

    def run_monte_carlo_simulation(self, formula_func, component_symbols, input_params, temperature, num_simulations=10000):
        """
        モンテカルロシミュレーションを実行し、指定された計算式の出力のばらつきを計算する。

        Args:
            formula_func (callable): 計算式を表す関数。引数として(component_values, input_params)を受け取る。
                                     component_valuesは{symbol: actual_value}の辞書。
                                     input_paramsはその他の入力パラメータの辞書。
            component_symbols (list): 計算式で使用するコンポーネントのシンボル名のリスト。
            input_params (dict): 計算式に渡すその他の入力パラメータの辞書。
            temperature (float): シミュレーションを行う温度（℃）。
            num_simulations (int): シミュレーション回数。

        Returns:
            dict: 計算式の出力の解析結果（公称値、平均値、最小値、最大値、標準偏差、パーセンテージ誤差など）。
        """
        # 公称値の計算
        nominal_component_values = {symbol: self.get_component(symbol).typ_value for symbol in component_symbols}
        nominal_output = formula_func(nominal_component_values, input_params)

        output_values = []
        for _ in range(num_simulations):
            # 各試行で計算式を評価
            try:
                output = self.evaluate_formula(formula_func, component_symbols, input_params, temperature)
                output_values.append(output)
            except ZeroDivisionError:
                # 分母が0になる場合はスキップ
                continue

        if not output_values:
            return {"error": "No valid output values could be calculated."}

        # 解析結果の計算
        avg_output = sum(output_values) / len(output_values)
        min_output = min(output_values)
        max_output = max(output_values)
        std_dev_output = (sum([(v - avg_output)**2 for v in output_values]) / len(output_values))**0.5

        # 公称値に対するパーセンテージ誤差
        percent_error_avg = ((avg_output - nominal_output) / nominal_output) * 100 if nominal_output != 0 else float('inf')
        percent_error_min = ((min_output - nominal_output) / nominal_output) * 100 if nominal_output != 0 else float('inf')
        percent_error_max = ((max_output - nominal_output) / nominal_output) * 100 if nominal_output != 0 else float('inf')

        return {
            "nominal_output": nominal_output,
            "average_output": avg_output,
            "min_output": min_output,
            "max_output": max_output,
            "std_dev_output": std_dev_output,
            "percent_error_average": percent_error_avg,
            "percent_error_min": percent_error_min,
            "percent_error_max": percent_error_max,
            "num_simulations": num_simulations
        }

    def perform_local_sensitivity_analysis(self, formula_func, component_symbols, input_params, temperature, delta=0.01):
        """
        計算式のパラメータに対する局所感度解析を行う。
        各コンポーネントの公称値を微小量変化させたときの出力の変化率を計算する。

        Args:
            formula_func (callable): 計算式を表す関数。引数として(component_values, input_params)を受け取る。
            component_symbols (list): 計算式で使用するコンポーネントのシンボル名のリスト。
            input_params (dict): 計算式に渡すその他の入力パラメータの辞書。
            temperature (float): 解析を行う温度（℃）。
            delta (float): 各パラメータを変化させる微小量（パーセンテージ、例: 0.01は1%）。

        Returns:
            dict: 各コンポーネントの感度解析結果。
                  キーはコンポーネントのシンボル名、値は出力の変化率。
        """
        sensitivity_results = {}

        # 基準となる公称値での出力を計算
        nominal_component_values = {symbol: self.get_component(symbol).typ_value for symbol in component_symbols}
        base_output = formula_func(nominal_component_values, input_params)

        for symbol in component_symbols:
            component = self.get_component(symbol)
            if not component:
                raise ValueError(f"Component with symbol {symbol} not found.")

            original_typ_value = component.typ_value

            # +delta% 変化させた場合の出力
            component.typ_value = original_typ_value * (1 + delta / 100)
            output_plus_delta = formula_func(
                {s: self.get_component(s).typ_value for s in component_symbols},
                input_params
            )

            # -delta% 変化させた場合の出力
            component.typ_value = original_typ_value * (1 - delta / 100)
            output_minus_delta = formula_func(
                {s: self.get_component(s).typ_value for s in component_symbols},
                input_params
            )

            # typ_valueを元に戻す
            component.typ_value = original_typ_value

            # 感度を計算 (出力の変化量 / 入力の変化量)
            # 入力の変化量 = original_typ_value * (delta / 100) * 2
            # 出力の変化量 = output_plus_delta - output_minus_delta
            
            # 感度 = (出力の変化量 / 基準出力) / (入力の変化量 / 基準入力)
            # ここでは、(出力の変化量 / 基準出力) / (2 * delta / 100) とします
            if base_output != 0 and original_typ_value != 0:
                sensitivity = ((output_plus_delta - output_minus_delta) / base_output) / (2 * delta / 100)
            else:
                sensitivity = float('inf') # ゼロ除算の場合

            sensitivity_results[symbol] = sensitivity

        return sensitivity_results

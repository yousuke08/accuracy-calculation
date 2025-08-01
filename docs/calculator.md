# Calculator クラス

回路の誤差計算を行うクラスです。複数のコンポーネントインスタンスを管理し、合成誤差の計算を行います。

## 機能

- コンポーネントインスタンスの管理
- モンテカルロシミュレーションによる回路出力のばらつき計算
- 計算式の評価

## 使用方法

```python
from scripts.calculator import Calculator

# コンポーネントのパラメータリスト
component_params = [
    {
        "symbol": "R1",
        "typ_value": 1000, # 1kΩ
        "room_temp_tolerance": 1, # ±1%
        "temp_coefficient": 50 # 50ppm/℃
    },
    {
        "symbol": "R2",
        "typ_value": 1000, # 1kΩ
        "room_temp_tolerance": 1, # ±1%
        "temp_coefficient": 50 # 50ppm/℃
    },
    {
        "symbol": "Vin",
        "typ_value": 5.0, # 5V
        "room_temp_tolerance": 0.1, # ±0.1%
        "temp_coefficient": 10 # 10ppm/℃
    }
]

# Calculatorインスタンスの作成
calculator = Calculator(component_params)

# 分圧回路の計算式を定義
def voltage_divider_formula(component_values, input_params):
    r1 = component_values["R1"]
    r2 = component_values["R2"]
    v_in = component_values["Vin"]
    if (r1 + r2) == 0:
        raise ZeroDivisionError("Denominator is zero")
    return v_in * (r2 / (r1 + r2))

# モンテカルロシミュレーションを実行
temperature = 25 # 常温
num_simulations = 10000

results = calculator.run_monte_carlo_simulation(
    formula_func=voltage_divider_formula,
    component_symbols=["R1", "R2", "Vin"],
    input_params={},
    temperature=temperature,
    num_simulations=num_simulations
)

print("公称出力:", results["nominal_output"])
print("平均出力:", results["average_output"])
print("最小出力:", results["min_output"])
print("最大出力:", results["max_output"])
print("出力の標準偏差:", results["std_dev_output"])
print("平均パーセンテージ誤差:", results["percent_error_average"])
print("最小パーセンテージ誤差:", results["percent_error_min"])
print("最大パーセンテージ誤差:", results["percent_error_max"])

# 特定の条件での計算式の評価
# 例えば、R1とR2の公称値、Vinの公称値で評価
nominal_output_eval = calculator.evaluate_formula(
    formula_func=voltage_divider_formula,
    component_symbols=["R1", "R2", "Vin"],
    input_params={},
    temperature=temperature # evaluate_formulaはばらつきを考慮しないので、温度は影響しないが引数として必要
)
print("公称値での評価結果:", nominal_output_eval)
```

## API

### `__init__(component_params_list)`

Calculatorクラスの初期化。
指定されたパラメータリストに基づいてComponentインスタンスを生成し、管理します。

#### 引数

- `component_params_list` (list): 各コンポーネントのパラメータを含む辞書のリスト。
                                  各辞書はComponentクラスの`__init__`に渡される引数に対応します。
                                  必須キー: `symbol`, `typ_value`, `room_temp_tolerance`, `temp_coefficient`
                                  オプションキー: `max_temp_tolerance`, `max_operating_temperature`, `sigma`, `seed`

### `get_component(symbol)`

指定されたシンボル名のComponentインスタンスを取得します。

#### 引数

- `symbol` (str): 取得するコンポーネントのシンボル名。

#### 戻り値

- `Component` または `None`: 指定されたシンボル名のComponentインスタンス。見つからない場合は`None`。

### `get_actual_component_value(symbol, temperature)`

指定されたシンボルのコンポーネントの、ばらつきを考慮した実際の値を取得します。

#### 引数

- `symbol` (str): コンポーネントのシンボル名。
- `temperature` (float): 現在の温度（℃）。

#### 戻り値

- `float`: ばらつきを考慮したコンポーネントの実際の値。

### `evaluate_formula(formula_func, component_symbols, input_params, temperature)`

指定された計算式を、現在のコンポーネントのばらつきと入力パラメータで評価します。

#### 引数

- `formula_func` (callable): 計算式を表す関数。引数として`(component_values, input_params)`を受け取ります。
                                     `component_values`は`{symbol: actual_value}`の辞書。
                                     `input_params`はその他の入力パラメータの辞書。
- `component_symbols` (list): 計算式で使用するコンポーネントのシンボル名のリスト。
- `input_params` (dict): 計算式に渡すその他の入力パラメータの辞書。
- `temperature` (float): 現在の温度（℃）。

#### 戻り値

- `float`: 計算式の評価結果。

### `run_monte_carlo_simulation(formula_func, component_symbols, input_params, temperature, num_simulations=10000)`

モンテカルロシミュレーションを実行し、指定された計算式の出力のばらつきを計算します。

#### 引数

- `formula_func` (callable): 計算式を表す関数。引数として`(component_values, input_params)`を受け取ります。
                                     `component_values`は`{symbol: actual_value}`の辞書。
                                     `input_params`はその他の入力パラメータの辞書。
- `component_symbols` (list): 計算式で使用するコンポーネントのシンボル名のリスト。
- `input_params` (dict): 計算式に渡すその他の入力パラメータの辞書。
- `temperature` (float): シミュレーションを行う温度（℃）。
- `num_simulations` (int): シミュレーション回数（デフォルト: 10000）。

#### 戻り値

- `dict`: 計算式の出力の解析結果。
  - `nominal_output` (float): 公称出力。
  - `average_output` (float): 平均出力。
  - `min_output` (float): 最小出力。
  - `max_output` (float): 最大出力。
  - `std_dev_output` (float): 出力の標準偏差。
  - `percent_error_average` (float): 平均パーセンテージ誤差。
  - `percent_error_min` (float): 最小パーセンテージ誤差。
  - `percent_error_max` (float): 最大パーセンテージ誤差。
  - `num_simulations` (int): シミュレーション回数。
  - `error` (str, optional): エラーが発生した場合のエラーメッセージ。

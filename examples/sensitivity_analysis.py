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

# 局所感度解析を実行
temperature = 25 # 常温
delta = 0.01 # 1%変化

sensitivity_results = calculator.perform_local_sensitivity_analysis(
    formula_func=voltage_divider_formula,
    component_symbols=["R1", "R2", "Vin"],
    input_params={},
    temperature=temperature,
    delta=delta
)

print("--- 局所感度解析結果 ---")
for symbol, sensitivity in sensitivity_results.items():
    print(f"シンボル: {symbol}, 感度: {sensitivity:.4f}")

# --- 理論感度（相対感度）の計算 --- 
# 分圧回路の出力電圧 Vout = Vin * (R2 / (R1 + R2))
# 相対感度 S_x^y = (dy/y) / (dx/x) = (dy/dx) * (x/y)
#
# R1に対する相対感度 S_R1^Vout = -R1 / (R1 + R2)
# R2に対する相対感度 S_R2^Vout = R1 / (R1 + R2)
# Vinに対する相対感度 S_Vin^Vout = 1

nominal_r1 = calculator.get_component("R1").typ_value
nominal_r2 = calculator.get_component("R2").typ_value
nominal_vin = calculator.get_component("Vin").typ_value

expected_sensitivity_r1 = -nominal_r1 / (nominal_r1 + nominal_r2)
expected_sensitivity_r2 = nominal_r1 / (nominal_r1 + nominal_r2)
expected_sensitivity_vin = 1.0

print("\n--- 理論感度（相対感度）---")
print(f"R1の理論感度: {expected_sensitivity_r1:.4f}")
print(f"R2の理論感度: {expected_sensitivity_r2:.4f}")
print(f"Vinの理論感度: {expected_sensitivity_vin:.4f}")

import pytest
from scripts.calculator import Calculator
from scripts.components import Component

def test_calculator_initialization():
    component_params = [
        {
            "symbol": "R1",
            "typ_value": 1000,
            "room_temp_tolerance": 1,
            "temp_coefficient": 50,
            "sigma": 3
        },
        {
            "symbol": "R2",
            "typ_value": 2000,
            "room_temp_tolerance": (-2, 2),
            "temp_coefficient": 100,
            "max_temp_tolerance": (-3, 3),
            "max_operating_temperature": 85
        },
        {
            "symbol": "Vref",
            "typ_value": 2.5,
            "room_temp_tolerance": 0.1,
            "temp_coefficient": 10,
            "sigma": 3
        }
    ]
    
    calculator = Calculator(component_params)
    
    assert "R1" in calculator.components
    assert "R2" in calculator.components
    assert "Vref" in calculator.components
    
    r1 = calculator.get_component("R1")
    assert isinstance(r1, Component)
    assert r1.typ_value == 1000
    assert r1.room_temp_tolerance == 1
    
    r2 = calculator.get_component("R2")
    assert isinstance(r2, Component)
    assert r2.typ_value == 2000
    assert r2.room_temp_tolerance == (-2, 2)
    assert r2.max_temp_tolerance == (-3, 3)
    assert r2.max_operating_temperature == 85

    vref = calculator.get_component("Vref")
    assert isinstance(vref, Component)
    assert vref.typ_value == 2.5
    assert vref.room_temp_tolerance == 0.1

def test_get_non_existent_component():
    component_params = [
        {
            "symbol": "R1",
            "typ_value": 1000,
            "room_temp_tolerance": 1,
            "temp_coefficient": 50
        }
    ]
    calculator = Calculator(component_params)
    assert calculator.get_component("R3") is None

def test_evaluate_formula():
    component_params = [
        {
            "symbol": "R1",
            "typ_value": 1000,
            "room_temp_tolerance": 1,
            "temp_coefficient": 50
        },
        {
            "symbol": "Vcc",
            "typ_value": 5.0,
            "room_temp_tolerance": 0.5,
            "temp_coefficient": 20
        }
    ]
    calculator = Calculator(component_params)
    temperature = 25

    # 簡単な計算式: R1 * Vcc
    def simple_formula(component_values, input_params):
        return component_values["R1"] * component_values["Vcc"]

    result = calculator.evaluate_formula(simple_formula, ["R1", "Vcc"], {}, temperature)
    # 公称値での計算結果を期待
    assert result == pytest.approx(1000 * 5.0, rel=0.05) # ばらつきを考慮し、5%以内の誤差を許容

    # 誤差を考慮した値が返されることを確認（複数回実行してばらつきを確認）
    results_list = []
    for _ in range(100):
        results_list.append(calculator.evaluate_formula(simple_formula, ["R1", "Vcc"], {}, temperature))
    
    # ばらつきがあることを確認
    assert max(results_list) != min(results_list)


def test_run_monte_carlo_simulation_voltage_divider():
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
        }
    ]
    
    calculator = Calculator(component_params)
    input_voltage = 5.0
    temperature = 25 # 常温
    num_simulations = 10000

    # 分圧回路の計算式を定義
    def voltage_divider_formula(component_values, input_params):
        r1 = component_values["R1"]
        r2 = component_values["R2"]
        v_in = input_params["input_voltage"]
        if (r1 + r2) == 0:
            raise ZeroDivisionError("Denominator is zero")
        return v_in * (r2 / (r1 + r2))

    results = calculator.run_monte_carlo_simulation(
        formula_func=voltage_divider_formula,
        component_symbols=["R1", "R2"],
        input_params={'input_voltage': input_voltage},
        temperature=temperature,
        num_simulations=num_simulations
    )

    # 結果の検証（おおよその値で検証）
    assert "nominal_output" in results
    assert "average_output" in results
    assert "min_output" in results
    assert "max_output" in results
    assert "std_dev_output" in results
    assert "percent_error_average" in results
    assert "percent_error_min" in results
    assert "percent_error_max" in results
    assert "num_simulations" in results

    # 公称値の検証
    nominal_r1 = calculator.get_component("R1").typ_value
    nominal_r2 = calculator.get_component("R2").typ_value
    expected_nominal_v_out = input_voltage * (nominal_r2 / (nominal_r1 + nominal_r2))
    assert results["nominal_output"] == pytest.approx(expected_nominal_v_out)

    # 平均値が公称値に近いことを確認
    assert results["average_output"] == pytest.approx(results["nominal_output"], rel=0.05) # 5%以内の誤差を許容

    # 最小値が公称値より小さいことを確認
    assert results["min_output"] < results["nominal_output"]

    # 最大値が公称値より大きいことを確認
    assert results["max_output"] > results["nominal_output"]

    # 標準偏差が0より大きいことを確認
    assert results["std_dev_output"] > 0

    # パーセンテージ誤差が妥当な範囲にあることを確認
    assert -5 < results["percent_error_average"] < 5
    assert -5 < results["percent_error_min"] < 0
    assert 0 < results["percent_error_max"] < 5

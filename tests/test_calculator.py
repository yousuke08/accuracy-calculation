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
        }
    ]
    
    calculator = Calculator(component_params)
    
    assert "R1" in calculator.components
    assert "R2" in calculator.components
    
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

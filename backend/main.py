import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Union
import math

from scripts.calculator import Calculator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ComponentParam(BaseModel):
    symbol: str
    typ_value: float
    room_temp_tolerance: Union[float, list[float]]
    temp_coefficient: float
    max_temp_tolerance: Optional[Union[float, list[float]]] = None
    max_operating_temperature: Optional[float] = None
    sigma: Optional[float] = None
    seed: Optional[int] = None


class SimulationRequest(BaseModel):
    components: list[ComponentParam]
    formula_type: str  # "voltage_divider" | "custom_multiply" | "custom_add" | "custom_divide"
    component_symbols: list[str]
    temperature: float = 25.0
    num_simulations: int = 10000


class SensitivityRequest(BaseModel):
    components: list[ComponentParam]
    formula_type: str
    component_symbols: list[str]
    temperature: float = 25.0
    delta: float = 1.0


def build_formula(formula_type: str):
    if formula_type == "voltage_divider":
        def f(cv, ip):
            r1 = cv.get("R1", 1)
            r2 = cv.get("R2", 1)
            vin = cv.get("Vin", 1)
            denom = r1 + r2
            if denom == 0:
                raise ZeroDivisionError
            return vin * (r2 / denom)
        return f
    elif formula_type == "multiply":
        def f(cv, ip):
            result = 1.0
            for v in cv.values():
                result *= v
            return result
        return f
    elif formula_type == "add":
        def f(cv, ip):
            return sum(cv.values())
        return f
    elif formula_type == "divide":
        def f(cv, ip):
            vals = list(cv.values())
            if len(vals) < 2 or vals[1] == 0:
                raise ZeroDivisionError
            return vals[0] / vals[1]
        return f
    else:
        raise HTTPException(status_code=400, detail=f"Unknown formula_type: {formula_type}")


def build_calculator(components: list[ComponentParam]) -> Calculator:
    params_list = []
    for c in components:
        p = c.model_dump()
        tolerance = p["room_temp_tolerance"]
        if isinstance(tolerance, list):
            p["room_temp_tolerance"] = tuple(tolerance)
        max_tol = p.get("max_temp_tolerance")
        if isinstance(max_tol, list):
            p["max_temp_tolerance"] = tuple(max_tol)
        params_list.append(p)
    return Calculator(params_list)


def sanitize(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


@app.post("/simulate")
def simulate(req: SimulationRequest):
    try:
        calc = build_calculator(req.components)
        formula = build_formula(req.formula_type)
        result = calc.run_monte_carlo_simulation(
            formula_func=formula,
            component_symbols=req.component_symbols,
            input_params={},
            temperature=req.temperature,
            num_simulations=req.num_simulations,
        )
        return {k: sanitize(v) for k, v in result.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sensitivity")
def sensitivity(req: SensitivityRequest):
    try:
        calc = build_calculator(req.components)
        formula = build_formula(req.formula_type)
        result = calc.perform_local_sensitivity_analysis(
            formula_func=formula,
            component_symbols=req.component_symbols,
            input_params={},
            temperature=req.temperature,
            delta=req.delta,
        )
        return {k: sanitize(v) for k, v in result.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}

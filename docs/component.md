# Component クラス

電子回路の要素（抵抗、コンデンサ、インダクタなど）を表すクラスです。各要素の誤差を計算するために使用されます。

## 機能

- ランダムな誤差の計算
- 温度依存の誤差の計算
- 総合的な誤差の計算

## 使用方法

```python
from scripts.components import Component

# コンポーネントの作成（シード指定可）
resistor = Component(typ_value=1000, random_tolerance=5, temp_coefficient=100, seed=42)

# ランダムな誤差の取得
random_error = resistor.get_random_variation()

# 温度依存の誤差の計算 (50℃での誤差)
temp_error = resistor.get_temperature_variation(50)

# 総合的な誤差の計算 (50℃での誤差)
total_error = resistor.get_total_variation(50)
```

## API

### `__init__(typ_value, random_tolerance, temp_coefficient, seed=None)`

コンポーネントを初期化します。

#### 引数

- `typ_value` (float): 典型値
- `random_tolerance` (float): ランダムな誤差（％）
- `temp_coefficient` (float): 温度係数（ppm/℃）
- `seed` (int, optional): ランダムジェネレータのシード

### `get_random_variation()`

ランダムな誤差を取得します。

#### 戻り値

- float: ランダムな誤差（％）

### `get_temperature_variation(temperature)`

温度依存の誤差を計算します。

#### 引数

- `temperature` (float): 現在の温度（℃）

#### 戻り値

- float: 温度依存の誤差（％）

### `get_total_variation(temperature, random_variation=None)`

総合的な誤差を計算します。

#### 引数

- `temperature` (float): 現在の温度（℃）
- `random_variation` (float, optional): ランダムな誤差（％）。指定しない場合はランダムに生成される

#### 戻り値

- float: 総合的な誤差（％）
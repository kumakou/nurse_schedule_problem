from ortools.sat.python import cp_model
import pandas as pd

num_nurses = 10
num_shifts = 3
num_days = 7
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)

model = cp_model.CpModel()
shifts = {}

# 変数の定義
for nurse in all_nurses:
    for day in all_days:
        for shift in all_shifts:
            shifts[(nurse, day, shift)] = model.NewBoolVar(f"shift_{nurse}_{day}_{shift}")

# 各看護師は1日に1回しか勤務しない制約
for nurse in all_nurses:
    for day in all_days:
        model.Add(sum(shifts[(nurse, day, shift)] for shift in all_shifts) <= 1)

# 1回のシフトの必要人数を満たす制約
shift_requirements = {
    0: [3, 4],  # 日勤
    1: [2, 1],  # 夜勤
    2: [2, 1]   # 深夜
}
for day in all_days:
    for shift in all_shifts:
        model.Add(sum(shifts[(nurse, day, shift)] for nurse in all_nurses) >= shift_requirements[shift][0])
        model.Add(sum(shifts[(nurse, day, shift)] for nurse in all_nurses) <= shift_requirements[shift][1])

# 1人あたりの週の勤務時間が5日以内の制約
max_shifts_per_nurse = 5
for nurse in all_nurses:
    model.Add(sum(shifts[(nurse, day, shift)] for day in all_days for shift in all_shifts) <= max_shifts_per_nurse)

# ソルバーを作成して解を求める
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 解が得られた場合、結果を表示する
if status == cp_model.OPTIMAL:
    schedule = []
    for day in all_days:
        day_schedule = {"日付": day}
        for shift in all_shifts:
            nurses = []
            for nurse in all_nurses:
                if solver.Value(shifts[(nurse, day, shift)]) == 1:
                    nurses.append(nurse)
            day_schedule[f"シフト {shift}"] = nurses
        schedule.append(day_schedule)

    df_schedule = pd.DataFrame(schedule)
    print(df_schedule)

from ortools.sat.python import cp_model
import pandas as pd

#ナースの数
num_nurses = 10
#シフトの数
num_shifts = 3
#日数
num_days = 7
#それぞれの長さ
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)

# モデルの定義
model = cp_model.CpModel()
shifts={}

required_nurses = pd.read_csv('required_num.csv', index_col=0)   
required_nurses = required_nurses.values.tolist()

# 各看護師は1日に1回しか勤務しない制約
for day in all_days:
    for nurse in all_nurses:
        shifts[(day, nurse)] = {}
        for shift in all_shifts:
            shifts[(day, nurse)][shift] = model.NewBoolVar(f"shift_d{day}_n{nurse}_s{shift}")
        model.Add(sum(shifts[(day, nurse)].values()) <= 1)

# 1回のシフトの必要人数を満たす制約
for day in all_days:
    for shift in all_shifts:
        shift_vars = []
        for nurse in all_nurses:
            shift_vars.append(shifts[(day, nurse)][shift])
        model.Add(sum(shift_vars) == required_nurses[day][shift])

# 1人あたりの週の勤務時間が5日以内の制約
for nurse in all_nurses:
    total_workdays = 0
    for day in all_days:
        for shift in all_shifts:
            total_workdays += shifts[(day, nurse)][shift]
    model.Add(total_workdays <= 5)


# ソルバーを作成して解を求める
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 解が得られた場合結果を表示する
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(solver.ObjectiveValue())
    for day in all_days:
        print(f"Day {day + 1}:")
        for shift in all_shifts:
            if shift == 0:
                print("  日勤", end=": ")
            elif shift == 1:
                print("  夜勤", end=": ")
            else:
                print("  深夜", end=": ")
            nurses_on_shift = []
            for nurse in all_nurses:
                if solver.Value(shifts[(day, nurse)][shift]):
                    nurse_number = nurse + 1
                    nurses_on_shift.append(nurse_number)
            print("ナース番号", nurses_on_shift)
    nurse_workdays = {nurse: 0 for nurse in all_nurses}
    for day in all_days:
        for nurse in all_nurses:
            for shift in all_shifts:
                if solver.Value(shifts[(day, nurse)][shift]):
                    nurse_workdays[nurse] += 1
    for nurse, workdays in nurse_workdays.items():
        print(f" ナース{nurse + 1}番は{workdays}日働いています")
else:
    print("解がないです")



model.Add(sum(shift_vars) == required_nurses[day][shift])
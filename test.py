import pulp

# 1. 定义车站列表
stations = ["London", "Tonbridge", "Ashford", "Canterbury", "Dover", "Margate"]
n = len(stations)

# 2. 输入需求数据 (Table 1)
# 格式: demand[i][j] 表示从 i 到 j 的需求
demand_data = {
    "London": {"Tonbridge": 100, "Ashford": 120, "Canterbury": 160, "Dover": 170, "Margate": 200},
    "Tonbridge": {"Ashford": 155, "Canterbury": 100, "Dover": 145, "Margate": 160},
    "Ashford": {"Canterbury": 150, "Dover": 105, "Margate": 125},
    "Canterbury": {"Dover": 185, "Margate": 165},
    "Dover": {"Margate": 155}
}

# 3. 输入票价数据 (Table 2)
fare_data = {
    "London": {"Tonbridge": 15, "Ashford": 18, "Canterbury": 19.5, "Dover": 36, "Margate": 52.5},
    "Tonbridge": {"Ashford": 16.5, "Canterbury": 18, "Dover": 29, "Margate": 46},
    "Ashford": {"Canterbury": 9, "Dover": 15.5, "Margate": 32.5},
    "Canterbury": {"Dover": 9.5, "Margate": 16.5},
    "Dover": {"Margate": 10.5}
}

# 4. 创建优化问题
prob = pulp.LpProblem("TrainEast_Revenue_Maximization", pulp.LpMaximize)

# 5. 定义决策变量 x[i,j]
x = {}
for i in range(n):
    for j in range(i + 1, n):
        start = stations[i]
        end = stations[j]
        # 变量：起始站到终点站的座位分配数，类型为整数
        x[i, j] = pulp.LpVariable(f"x_{i}_{j}", lowBound=0,
                                  upBound=demand_data[start][end],
                                  cat='Integer')

# 6. 目标函数：最大化总收益
prob += pulp.lpSum(x[i, j] * fare_data[stations[i]][stations[j]]
                   for i in range(n) for j in range(i + 1, n))

# 7. 添加容量约束 (Capacity = 500)
# 列车共有 n-1 个物理路段：(0,1), (1,2), (2,3), (3,4), (4,5)
capacity = 500
for k in range(n - 1):
    # 对于每一个路段 (k, k+1)，计算当前在车上的所有人
    # 乘客从 i 上车，j 下车，如果 i <= k 且 j >= k+1，则他们在路段 k 上
    prob += pulp.lpSum(x[i, j] for i in range(k + 1) for j in range(k + 1, n)) <= capacity, f"Cap_Constraint_Segment_{k}"

# 8. 求解
prob.solve(pulp.PULP_CBC_CMD(msg=0))

# 9. 输出结果
print(f"优化状态: {pulp.LpStatus[prob.status]}")
print(f"最大总收入: £{pulp.value(prob.objective):,.2f}")
print("\n详细分配方案:")
print("-" * 40)
for i in range(n):
    for j in range(i + 1, n):
        val = pulp.value(x[i, j])
        if val > 0:
            print(f"{stations[i]:<10} -> {stations[j]:<10} : 分配 {int(val):>3} 座 (需求: {demand_data[stations[i]][stations[j]]})")
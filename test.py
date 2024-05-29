def solve_task(num: int) -> int:
    sum = 0
    for i in range(num):
        t = input()
        if t[-1] == '4':
            sum += int(t)
    return sum

if __name__ == '__main__':
    print(solve_task(int(input())))
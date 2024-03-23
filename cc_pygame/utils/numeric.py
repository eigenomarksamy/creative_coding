def get_lcd(num1: int, num2: int) -> int:
    divisor = 1
    for i in range(2, min(num1, num2)):
        if num2 % i == 0 and num1 % i == 0:
            divisor = i
            break
    return divisor

def get_hcd(num1: int, num2: int) -> int:
    divisor = 1
    for i in range(min(num1, num2), 1, -1):
        if num2 % i == 0 and num1 % i == 0:
            divisor = i
            break
    return divisor
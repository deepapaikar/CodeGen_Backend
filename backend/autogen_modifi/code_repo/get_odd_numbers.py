# filename: get_odd_numbers.py

def get_odd_numbers_under_50():
    odd_numbers = []
    for number in range(1, 50):
        if number % 2 == 1:
            odd_numbers.append(number)
    return odd_numbers

# Example usage:
if __name__ == "__main__":
    odd_numbers = get_odd_numbers_under_50()
    print(odd_numbers)
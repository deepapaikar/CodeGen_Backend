# filename: prime_numbers_0_to_100.py

def is_prime(num):
    """Check if a number is a prime number."""
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def print_primes(start, end):
    """Print all prime numbers in a given range."""
    for number in range(start, end + 1):
        if is_prime(number):
            print(number, end=' ')
    print()  # for a new line after printing all primes

# Print prime numbers between 0 and 100
print_primes(0, 100)
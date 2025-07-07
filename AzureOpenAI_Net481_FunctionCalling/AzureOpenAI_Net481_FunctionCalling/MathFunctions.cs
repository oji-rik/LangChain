using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;

namespace AzureOpenAI_Net481_FunctionCalling
{
    public static class MathFunctions
    {
        public static List<int> PrimeFactorization(int n)
        {
            if (n <= 1) throw new ArgumentException("Number must be greater than 1");
            
            var factors = new List<int>();
            for (int i = 2; i * i <= n; i++)
            {
                while (n % i == 0)
                {
                    factors.Add(i);
                    n /= i;
                }
            }
            if (n > 1) factors.Add(n);
            return factors;
        }

        public static int Sum(List<int> numbers)
        {
            if (numbers == null) throw new ArgumentNullException(nameof(numbers));
            return numbers.Sum();
        }

        public static int Multiply(List<int> numbers)
        {
            if (numbers == null) throw new ArgumentNullException(nameof(numbers));
            if (numbers.Count == 0) return 0;
            
            int result = 1;
            foreach (int num in numbers)
            {
                result *= num;
            }
            return result;
        }

        public static double Divide(double dividend, double divisor)
        {
            if (Math.Abs(divisor) < double.Epsilon)
                throw new ArgumentException("Cannot divide by zero");
            return dividend / divisor;
        }

        public static double Power(double baseNumber, double exponent)
        {
            return Math.Pow(baseNumber, exponent);
        }

        public static string Factorial(int n)
        {
            if (n < 0) throw new ArgumentException("Factorial is not defined for negative numbers");
            if (n > 1000) throw new ArgumentException("Factorial calculation limit exceeded (maximum: 1000)");
            
            BigInteger result = 1;
            for (int i = 2; i <= n; i++)
            {
                result *= i;
            }
            return result.ToString();
        }

        public static int Gcd(int a, int b)
        {
            a = Math.Abs(a);
            b = Math.Abs(b);
            
            while (b != 0)
            {
                int temp = b;
                b = a % b;
                a = temp;
            }
            return a;
        }

        public static int Lcm(int a, int b)
        {
            if (a == 0 || b == 0) return 0;
            return Math.Abs(a * b) / Gcd(a, b);
        }

        public static bool IsPrime(int n)
        {
            if (n <= 1) return false;
            if (n <= 3) return true;
            if (n % 2 == 0 || n % 3 == 0) return false;
            
            for (int i = 5; i * i <= n; i += 6)
            {
                if (n % i == 0 || n % (i + 2) == 0)
                    return false;
            }
            return true;
        }

        public static double SquareRoot(double number)
        {
            if (number < 0) throw new ArgumentException("Cannot calculate square root of negative number");
            return Math.Sqrt(number);
        }

        public static double Absolute(double number)
        {
            return Math.Abs(number);
        }

        public static int Modulo(int dividend, int divisor)
        {
            if (divisor == 0) throw new ArgumentException("Cannot perform modulo with zero divisor");
            return dividend % divisor;
        }

        public static int Max(List<int> numbers)
        {
            if (numbers == null) throw new ArgumentNullException(nameof(numbers));
            if (numbers.Count == 0) throw new ArgumentException("List cannot be empty");
            return numbers.Max();
        }

        public static int Min(List<int> numbers)
        {
            if (numbers == null) throw new ArgumentNullException(nameof(numbers));
            if (numbers.Count == 0) throw new ArgumentException("List cannot be empty");
            return numbers.Min();
        }

        public static double Average(List<int> numbers)
        {
            if (numbers == null) throw new ArgumentNullException(nameof(numbers));
            if (numbers.Count == 0) throw new ArgumentException("List cannot be empty");
            return numbers.Average();
        }
    }
}
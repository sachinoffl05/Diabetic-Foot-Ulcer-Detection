package programs;

import java.util.Scanner;

public class factorial {
    static int f(int n){
        int c=1;
        for(int i=1;i<=n;i++){
            c=c*i;
        }
        return c;
    }
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        System.out.println(f(a));
    }
}
/*class FactorialRecursion {

    static int fact(int n) {
        if (n == 0 || n == 1)
            return 1;          // Base case
        else
            return n * fact(n - 1);  // Recursive call
    }

    public static void main(String[] args) {

        int n = 5;

        System.out.println("Factorial = " + fact(n));
    }
}
 */
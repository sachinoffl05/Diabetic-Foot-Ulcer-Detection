package programs;

import java.util.Scanner;

public class Fibonacci {
    static int f(int n){
        if(n<=1){
            return n;
        }
        else{
            return f(n-1)+f(n-2);
        }
    }
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        for(int i=0;i<a;i++){
            System.out.print(f(i)+" ");
        }
    }
}

/*class Fibonacci {
    public static void main(String[] args) {

        int n = 6;

        int a = 0;  // First number
        int b = 1;  // Second number

        for (int i = 0; i < n; i++) {
            System.out.print(a + " ");

            int next = a + b; // Next Fibonacci number
            a = b;            // Shift values
            b = next;
        }
    }
}
*/
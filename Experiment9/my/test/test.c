#include <stdio.h>
#include <math.h>

void occupy_cpu() {
    while (1) {
        // 执行一些耗时的计算，以占用 CPU
        double result = 0;
        int i;
        for (i = 0; i < 1000000; ++i) {
            result += sqrt(i);
        }
    }
}

int main() {
    occupy_cpu();
    return 0;
}

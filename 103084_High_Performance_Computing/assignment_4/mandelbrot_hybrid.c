/*
 * mandelbrot-seq.c
 * 
 *
 * The Mandelbrot calculation is to iterate the equation
 * z = z*z + c, where z and c are complex numbers, z is initially
 * zero, and c is the coordinate of the point being tested. If
 * the magnitude of z remains less than 2 for ever, then the point
 * c is in the Mandelbrot set. In this code We write out the number of iterations
 * before the magnitude of z exceeds 2, or UCHAR_MAX, whichever is
 * smaller.
*/

#include <stdio.h>
#include <mpi.h>
#include <omp.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>

void color(int red, int green, int blue)
{
    fputc((char)red, stdout);
    fputc((char)green, stdout);
    fputc((char)blue, stdout);
}

void printFractal(int numProcessor, int numColumns){
    int *buffer = malloc(numColumns*sizeof(int));
    MPI_Status status;
    int i,j;
    for (i = 1; i < numProcessor; i++){    
        int columns = numColumns/(numProcessor-1);
        int extraColumns = numColumns % (numProcessor-1);
        int initial = columns * (i-1);
        int end = columns + initial;
        if(i == numProcessor-1){
            end += extraColumns;
        }
        MPI_Recv(buffer,end-initial,MPI_INT,i,0,MPI_COMM_WORLD,&status);
        for(j = 0; j < end-initial;j++){
            if(buffer[j]== 0){
                color(0,0,0);
            }else{
                color(buffer[j],buffer[j],255);
            }
        }
    }

}

int main(int argc, char *argv[])
{
    /* int w = 600, h = 400, x, y; */
    int w = 600, h = 400, x, y;
    
    /* each iteration, it calculates: newz = oldz*oldz + p, where p is the 
       current pixel, and oldz stars at the origin */
    double pr, pi;                            /* real and imaginary part of the pixel p    */
    double newRe, newIm, oldRe, oldIm;        /* real and imaginary parts of new and old z */
    double zoom = 1, moveX = -0.5, moveY = 0; /* you can change these to zoom and change position */
    int maxIterations = 10000;               /* function stops after maxIterations */
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    clock_t begin, end;
    double time_spent;
    
    if(rank == 0){
        printf("P6\n# CREATOR: Eric R. Weeks / mandel program\n");
        printf("%d %d\n255\n",w,h);
        fprintf(stderr,"mpi%d\n",size);
    }
    
    begin = clock();
    
    /* loop through every pixel */
    for(y = 0; y < h; y++) {
        if(rank == 0){
            printFractal(size,w);
        }else{
            int array[w];
            int columns = w/(size-1);
            int extraColumns = w % (size-1);
            int initial = columns * (rank-1);
            int end = columns+initial;
            if(rank == size-1){
                end += extraColumns;
            }
            #pragma omp parallel for private(x, pr, pi, newRe, newIm, oldRe, oldIm)
            for(x = initial; x < end; x++) {
                // fprintf(stderr,"threads%d\n",omp_get_num_threads());
                /* 'i' will represent the number of iterations */
                int i;
                
                /* calculate the initial real and imaginary part of z, based on the
                pixel location and zoom and position values */
                pr = 1.5 * (x - w / 2) / (0.5 * zoom * w) + moveX;
                pi = (y - h / 2) / (0.5 * zoom * h) + moveY;
                newRe = newIm = oldRe = oldIm = 0.0; /* these should start at 0.0 */
                
                /* start the iteration process */
                for(i = 0; i < maxIterations; i++) {
                    /* remember value of previous iteration */
                    oldRe = newRe;
                    oldIm = newIm;
                    /* the actual iteration, the real and imaginary part are calculated */
                    newRe = oldRe * oldRe - oldIm * oldIm + pr;
                    newIm = 2 * oldRe * oldIm + pi;
                    /* if the point is outside the circle with radius 2: stop */
                    if((newRe * newRe + newIm * newIm) > 4) break;
                }

                if(i == maxIterations) {
                    array[x-initial] = 0;
                } else {
                    double z = sqrt(newRe * newRe + newIm * newIm);
                    int brightness = 256 * log2(1.75 + i - log2(log2(z))) / log2((double)maxIterations);
                    array[x-initial] = brightness;
                }
            }
            // fprintf(stderr,"init=%d  end=%d \n",initial,end);
            MPI_Send(array,end-initial,MPI_INT,0,0,MPI_COMM_WORLD);
            
        }
    }
    
    end = clock();
    if(rank==0){
        time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
        fprintf(stderr, "Elapsed time: %.2f seconds.\n", time_spent);
    }


    MPI_Finalize();
    return 0;
}
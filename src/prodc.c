#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include </usr/include/semaphore.h>

#define BUFF_SIZE   5
#define NP          3
#define NC          3
#define NITERS      10

typedef struct {
	int buf[BUFF_SIZE];
	int in; //is the first empty slot
	int out; //is the first full slot

	int produced_count;
	sem_t full;
	sem_t empty;
	sem_t mutex;

} sbuf_t;

sbuf_t shared_buff;

void *Producer(void *arg) {
	int i, item, index;

	index = (int) arg;
	for (i = 0; i < NITERS; i++) {
		item = i; //Produce item

		sem_wait(&shared_buff.empty); //If there are no empty slots
		sem_wait(&shared_buff.mutex); //If another thread uses the buffer, wait
		shared_buff.buf[shared_buff.in] = item;
		printf("[P%d] Producing %d ...\n", index, item);
		fflush(stdout);
		++shared_buff.produced_count;
		++shared_buff.in;
		sem_post(&shared_buff.mutex); // Release the buffer
		sem_post(&shared_buff.full); // Increment the number of full slots

		if (i % 2 == 1)
			sleep(1); // Interleave  producer and consumer execution
	}

	printf("[P%d] Producer leaving \n", index);
	fflush(stdout);
	return NULL;
}

void *Consumer(void *arg) {
	int item, index;
	index = (int) arg;

	while (1) {
		sem_wait(&shared_buff.full);
		sem_wait(&shared_buff.mutex);
		item = shared_buff.buf[shared_buff.in - 1];
		printf("[C%d] Consuming %d ...\n", index, item);
		fflush(stdout);
		--shared_buff.in;
		sem_post(&shared_buff.mutex);
		sem_post(&shared_buff.empty);
	}
	printf("[P%d] Consumer leaving \n", index);
	fflush(stdout);
}

int main() {
	pthread_t idP, idC;
	int index;

	shared_buff.in = 0;
	shared_buff.out = -1;
	shared_buff.produced_count = 0;

	for (index = 0; index < BUFF_SIZE; index++) {
		shared_buff.buf[index] = -1;
	}

	sem_init(&shared_buff.full, 0, 0);
	sem_init(&shared_buff.empty, 0, BUFF_SIZE);

	sem_init(&shared_buff.mutex, 0, 1); //Insert code here to initialize mutex

	pthread_create(&idP, NULL, Producer, 0);
	pthread_create(&idC, NULL, Consumer, 0);

	pthread_exit(NULL);
}

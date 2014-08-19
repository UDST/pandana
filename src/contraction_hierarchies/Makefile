################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-all: libch.a

# Tool invocations
libch.a: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	$(CXX) -DLINUX -DMAC -std=c++0x -c -fPIC -g -O3 -Wall -pedantic -fopenmp \
		-I. -I.. -o libch.o src/libch.cpp #-stdlib=libc++
	@echo 'Invoking: GCC Archiver'
	ar -r  "libch.a" libch.o
	@echo 'Finished building target: $@'
	@echo ' '

# Other Targets
clean:
	rm -rf libch.a
	rm -rf *.o

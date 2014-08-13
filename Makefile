# set the target for ann
ifeq ($(shell uname), Darwin)
	build := macosx-g++
else
	build := linux-g++
endif

TARGET = all

all:
	cd ann_1.1.2; $(MAKE) $(build)
	cd sparsehash-2.0.2; ./configure; $(MAKE)
	$(MAKE) -C contraction_hierarchies

clean:
	cd ann_1.1.2; $(MAKE) clean
	cd sparsehash-2.0.2; $(MAKE) clean
	cd contraction_hierarchies; $(MAKE) clean

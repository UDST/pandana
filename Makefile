TARGET = all
all:
	cd ann_1.1.2; $(MAKE) linux-g++
	cd sparsehash-2.0.2; ./configure; $(MAKE)
	$(MAKE) -C contraction_hierarchies
clean:
	cd ann_1.1.2; $(MAKE) clean
	cd sparsehash-2.0.2; $(MAKE) clean
	cd contraction_hierarchies; $(MAKE) clean

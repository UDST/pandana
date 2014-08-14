TARGET = all
all:
	cd ann_1.1.2; $(MAKE) linux-g++
	$(MAKE) -C contraction_hierarchies
clean:
	cd ann_1.1.2; $(MAKE) clean
	cd contraction_hierarchies; $(MAKE) clean

IDIR =../include
CC=gcc
CFLAGS=-I$(IDIR) -DBMI08X_ENABLE_BMI085=0 -DBMI08X_ENABLE_BMI088=1

ODIR=obj
LDIR =../lib

LIBS=-lm

_DEPS = bmi088.h bmi08x.h bmi08x_defs.h rpi_i2c.h rpi_bmi088.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = bmi088.o bmi08a.o bmi08g.o rpi_i2c.o rpi_bmi088.o print_bmi088.o    
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

BMI088_read: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 
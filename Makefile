CC=gcc
INC_DIR=inc
DEST_DIR=src/bin
CC_ARGS= -fPIC -shared -Wall -Wextra -Wpedantic

all:
	@mkdir -p $(DEST_DIR)
	$(CC) $(CC_ARGS) -o $(DEST_DIR)/pid.so $(INC_DIR)/pid/*.c
	$(CC) $(CC_ARGS) -o $(DEST_DIR)/modbus.so $(INC_DIR)/modbus/*.c

clean:
	rm $(DEST_DIR)/*.so

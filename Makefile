INC_DIR=inc
DEST_DIR=src/bin

all:
	gcc -fPIC -shared -o $(DEST_DIR)/pid.so $(INC_DIR)/pid/*.c
	gcc -fPIC -shared -o $(DEST_DIR)/modbus.so $(INC_DIR)/modbus/*.c

clean:
	rm $(DEST_DIR)/*.so

.PHONY: .gdbinit
export sym_file_path
export exec_address
export iris_port
run:.gdbinit
.gdbinit:.gdbinit.tmp

	sed "s/<sym-file>/$(sym_file_path)/" < $^ | \
	sed "s/<offset>/$(exec_address)/" > $@

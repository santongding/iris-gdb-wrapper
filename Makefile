.PHONY: .gdbinit
export sym_file_path
export fvp_cmd
run:.gdbinit
.gdbinit:.gdbinit.tmp

	sed "s/<sym-file>/$(sym_file_path)/" < $^ > $@

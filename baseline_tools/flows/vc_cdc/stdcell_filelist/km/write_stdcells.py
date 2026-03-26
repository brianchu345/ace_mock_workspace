#!/usr/intel/pkgs/python3/3.10.8/bin/python3

import os

stdcell_main_dir = ["/p/hdk/cad/stdcells/lib786_i0m_180h_50pp/pdk050_r0v2p0_efv", "/p/hdk/cad/stdcells/lib786_i0s_160h_50pp/pdk050_r0v2p0_efv"]
stdcell_filelist = "stdcells.f"
with open(stdcell_filelist, "w") as wh:
    for stdcell_dir in stdcell_main_dir:
        lib_dirs = os.listdir(stdcell_dir)
        for libdir in lib_dirs:
            verilog_path = os.path.join(stdcell_dir, libdir, "verilog")
            if os.path.exists(verilog_path):
                files = os.listdir(verilog_path)
                for file in files:
                    if file.endswith(libdir + ".v"):
                        wh.write(verilog_path + "/" + file + "\n")
            

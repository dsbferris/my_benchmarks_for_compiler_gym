import requests
import tarfile
import subprocess
import pathlib
import os
import shutil
import time

import gym
from compiler_gym.envs.llvm import make_benchmark
from compiler_gym.envs.llvm.llvm_env import Benchmark

class Sqlite():
    def __init__(self) -> None:
        self.link = "http://www.phoronix-test-suite.com/benchmark-files/sqlite-330-for-speedtest.tar.gz"
        self.file_sha256 = "7ce167db515e3ea48681a2cbcf62f454cdaa181a25b376d4123f532cfbe3e510"
        self.file_md5 = "2f18e8fa835b7a6d7366bc6109614031"
        #self.filename = "sqlite-330-for-speedtest.tar.gz"
        self.filename = self.link.split("/")[-1]
        self.folder = "./sqlite"
        if not self.isArchiveFileExisting():
            self.downloadAndVerify()
        if not self.isFolderExisiting():
            self.unpack()
        if not self.isMakefileExisiting():
            self.run_configure()
        if not self.isSqlite3DOTcExisiting():
            self.run_make_clean()
            self.run_make_sqlite3DOTc()
        

    def isFolderExisiting(self) -> bool:
        return pathlib.Path(self.folder).exists()

    def isArchiveFileExisting(self) -> bool:
        return pathlib.Path(self.filename).exists()

    def isMakefileExisiting(self) -> bool:
        return pathlib.Path(os.path.join(self.folder, "Makefile")).exists()
        
    def isSqlite3DOTcExisiting(self) -> bool:
        return pathlib.Path(os.path.join(self.folder, "sqlite3.c")).exists()
        

    def downloadAndVerify(self):
        print("Downloading sqlite test...")
        if (which := shutil.which("curl")) is not None:
            subprocess.run([which, "-O", self.link])
        elif (which := shutil.which("wget")) is not None:
            subprocess.run([which, self.link])
        else:
            with requests.get(self.link, allow_redirects=True) as response:
                print("Writing download to file...")
                with open(self.filename, "wb") as f:
                    f.write(response.content)
                    print("Finished writing")
        print("Verifying download...")
        hash = HashingHelper(filepath=self.filename)
        assert hash.get_md5() == self.file_md5
        assert hash.get_sha256() == self.file_sha256
        print("Hashes match! Download succeeded.")

    def unpack(self):
        if not self.isArchiveFileExisting():
            raise Exception("No file to unpack! Did you forget to download first?")
        
        if self.isFolderExisiting():
            print("Folder already exists. Will delete existing folder and unpack then.")
            os.rmdir(self.folder)
            
        print("Unpacking sqlite test...")
        start = time.time_ns()
        with tarfile.open(self.filename) as f:
            f.extractall()  # if we give folder "sqlite" here, it will duplicate the sqlite folder
        diff = time.time_ns() - start
        print(f"Finished unpacking. This took {diff/10**9}s\n")
        
    def run_configure(self):
        os.chdir(self.folder)
        print("Running configure...")
        start = time.time_ns()
        completed_process = subprocess.run(["./configure", "CC=clang", "CFLAGS=-O2"])
        diff = time.time_ns() - start
        os.chdir("..")
        print("Return code: {0}".format(completed_process.returncode))
        print(f"Finished configure. This took {'{:0.2f}'.format(diff/10**9)}s\n")

    def run_make_clean(self):
        os.chdir(self.folder)
        print("Running make clean...")
        start = time.time_ns()
        completed_process = subprocess.run(["make", "clean"])
        diff = time.time_ns() - start
        os.chdir("..")
        print("Return code: {0}".format(completed_process.returncode))
        print(f"Finished make clean. This took {'{:0.2f}'.format(diff/10**9)}s\n")

    def run_make_sqlite3DOTc(self):
        os.chdir(self.folder)
        print("Running make sqlite3.c...")
        start = time.time_ns()
        completed_process = subprocess.run(["make", "sqlite3.c"])
        diff = time.time_ns() - start
        os.chdir("..")
        print("Return code: {0}".format(completed_process.returncode))
        print(f"Finished make sqlite3.c. This took {'{:0.2f}'.format(diff/10**9)}s\n")

    def run_clang_speedtest(self):
        compile_str = "clang -o speedtest1 -O2 -DSQLITE_THREADSAFE=1 -I. test/speedtest1.c sqlite3.c"
        os.chdir(self.folder)
        print("Running clang speedtest1...")
        # start = time.perf_counter_ns()
        start = time.time_ns()
        completed_process = subprocess.run(compile_str.split())
        # diff = time.perf_counter_ns() - start
        diff = time.time_ns() - start
        os.chdir("..")
        print("Return code: {0}".format(completed_process.returncode))
        print(f"Finished clang speedtest1. This took {'{:0.2f}'.format(diff/10**9)}s\n")

    def make_benchmark(self):
        speedtest1_filepath = pathlib.Path(os.path.join(self.folder, "test", "speedtest1.c"))
        sqlite3_filepath = pathlib.Path(os.path.join(self.folder, "sqlite3.c"))
        compile_copt= f"-I{pathlib.Path(self.folder).resolve()} \
            -D_HAVE_SQLITE_CONFIG_H -DBUILD_sqlite -DNDEBUG -DSQLITE_THREADSAFE=1 -DSQLITE_HAVE_ZLIB=1"
        print("Running make_benchmark...")
        # start = time.perf_counter_ns()
        start = time.time_ns()
        benchmark: Benchmark = make_benchmark([speedtest1_filepath, sqlite3_filepath], 
                                              system_includes=True, copt=compile_copt.split())
        # diff = time.perf_counter_ns() - start
        diff = time.time_ns() - start
        print(f"Finished make_benchmark. This took {'{:0.2f}'.format(diff/10**9)}s\n")
        return benchmark
    
    def make_env_with_benchmark(self, llvm_env: str) -> gym.Env:
        print("Running make env with benchmark...")
        start = time.time_ns()
        env = gym.make(llvm_env)
        env.reset(self.make_benchmark())
        diff = time.time_ns() - start
        print(f"Finished make env with benchmark. This took {'{:0.2f}'.format(diff/10**9)}s\n")
        return env
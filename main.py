from sqlite import Sqlite
import gym
import phoronix_parser

memcached_xml_link = "https://raw.githubusercontent.com/phoronix-test-suite/phoronix-test-suite/master/ob-cache/test-profiles/pts/memcached-1.1.0/downloads.xml"

sqlite_xml_link = "https://github.com/phoronix-test-suite/phoronix-test-suite/blob/master/ob-cache/test-profiles/pts/sqlite-speedtest-1.0.1/downloads.xml"

memcached_xml_path = phoronix_parser.get_download_xml(memcached_xml_link)
memcached_packages = phoronix_parser.parse_downloads_xml(memcached_xml_path)
memcachd_folders = phoronix_parser.download_verify_untar_packages(memcached_packages)
pass


# prep = Sqlite()
# prep.run_clang_speedtest()
# benchmark = prep.make_benchmark()
# env = prep.make_env_with_benchmark("llvm-v0")
# env.close()




print("DONE")
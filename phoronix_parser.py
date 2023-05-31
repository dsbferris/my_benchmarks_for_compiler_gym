from pathlib import Path
import shutil
import subprocess
import requests
import hashing_helper
import os
import tarfile
import xml.etree.ElementTree as ET


def download(link: str, filename: str) -> Path:
    if (which := shutil.which("wget")) is not None:
        proc = subprocess.run([which,"-O", filename, link])
        if proc.returncode != 0:
            raise Exception("Error with curl!")
    elif (which := shutil.which("curl")) is not None:
        proc = subprocess.run([which, "-o", filename, link])
        if proc.returncode != 0:
            raise Exception("Error with curl!")
    else:
        with requests.get(link, allow_redirects=True) as response:
            print("Writing download to file...")
            with open(filename, "wb") as f:
                f.write(response.content)
                print("Finished writing")
    return Path(filename)

def get_download_xml(link: str) -> Path:
    link_split = link.split("/")
    filename = f"{link_split[-2]}_{link_split[-1]}"  
    if Path(filename).exists():
        os.remove(filename)
    if "downloads.xml" not in filename:
        raise Exception("Not a valid downloads.xml link!")
    else:
        return download(link=link, filename=filename)

def verify(filepath: Path, md5: str, sha256: str, size: int) -> bool:
    md5_and_sha256 = hashing_helper.get_md5_and_sha256(filepath=filepath)
    return md5_and_sha256[0] == md5 \
        and md5_and_sha256[1] == sha256 \
        and filepath.stat().st_size == size

def untar(filepath: Path) -> Path:
    with tarfile.open(filepath) as f:
        f.extractall()
        return Path(f.getnames()[0])
    

class Package():
    url: str
    md5: str
    sha256: str
    filesize: int
    filename: str
    
    def no_field_none(self) -> bool:
        return self.url is not None \
            and self.md5 is not None \
            and self.sha256 is not None \
            and self.filename is not None \
            and self.filesize is not None
    
    

def parse_downloads_xml(xml_filepath: Path) -> list[Package]:
    packages: list[Package] = []
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    for c1 in root:
        if c1.tag == "Downloads":
            for c2 in c1:
                if c2.tag == "Package":
                    p = Package()
                    for c3 in c2:
                        match c3.tag.lower():
                            case "url":
                                p.url = c3.text
                            case "md5":
                                p.md5 = c3.text
                            case "sha256":
                                p.sha256 = c3.text
                            case "filename":
                                p.filename = c3.text
                            case "filesize":
                                p.filesize = int(c3.text)
                    if p.no_field_none():
                        packages.append(p)
    if packages == []:
        raise Exception("Nothing found to download!")
    return packages


def download_verify_untar_packages(packages: list[Package]) -> list[Path]:
    paths: list[Path] = []
    for p in packages:
        filepath = Path(p.filename)
        if filepath.exists():
            os.remove(filepath)
        download(p.url, p.filename)
        if not verify(filepath, p.md5, p.sha256, p.filesize):
            raise Exception("Download corrupted!")
        paths.append(untar(filepath))
    return paths

    
""" Sample XML
<?xml version="1.0"?>
<!--Phoronix Test Suite v10.8.4-->
<PhoronixTestSuite>
    <Downloads>
        <Package>
        <URL>http://www.memcached.org/files/memcached-1.6.18.tar.gz</URL>
        <MD5>afddef72d2109619b89e482c2d6a4a4f</MD5>
        <SHA256>cbdd6ab8810649ac5d92fcd0fcb0ca931d8a9dbd0ad8cc575b47222eedd64158</SHA256>
        <FileName>memcached-1.6.18.tar.gz</FileName>
        <FileSize>1081928</FileSize>
        </Package>
        <Package>
        <URL>https://github.com/RedisLabs/memtier_benchmark/archive/refs/tags/1.4.0.tar.gz</URL>
        <MD5>536666de87f3db01bd83181d3cd2cea8</MD5>
        <SHA256>e154e1cc2e8bc99634c3a947a4dfad885de9d28a78e3cc18bcec6254f1aa4992</SHA256>
        <FileName>memtier_benchmark-1.4.0.tar.gz</FileName>
        <FileSize>315519</FileSize>
        </Package>
    </Downloads>
</PhoronixTestSuite>
"""

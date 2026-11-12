#!/usr/bin/env python3
"""Explicit local HTTP CONNECT transport for OpenSSH. Does not read SSH passwords."""
import argparse
import ipaddress
import socket
import sys
import threading


def proxy_address(value):
    host, separator, port = value.rpartition(":")
    host = host.strip("[]")
    if not separator or not ipaddress.ip_address(host).is_loopback:
        raise ValueError("SSH proxy must be an explicit loopback IP:port.")
    port = int(port)
    if not 1 <= port <= 65535:
        raise ValueError("Invalid local proxy port.")
    return host, port


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proxy", required=True)
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()
    target = ipaddress.ip_address(args.host)
    authority = ("[" + str(target) + "]" if target.version == 6 else str(target)) + ":" + str(args.port)
    with socket.create_connection(proxy_address(args.proxy), timeout=15) as connection:
        connection.sendall(("CONNECT " + authority + " HTTP/1.1\r\nHost: " +
                            authority + "\r\n\r\n").encode("ascii"))
        header = bytearray()
        while not header.endswith(b"\r\n\r\n") and len(header) < 8192:
            chunk = connection.recv(1)
            if not chunk:
                raise RuntimeError("Local proxy closed before CONNECT completed.")
            header.extend(chunk)
        first = bytes(header).split(b"\r\n", 1)[0].split()
        if len(first) < 2 or first[1] != b"200":
            raise RuntimeError("Local proxy refused HTTP CONNECT.")
        connection.settimeout(None)

        def upstream():
            try:
                while True:
                    data = sys.stdin.buffer.read1(65536)
                    if not data:
                        break
                    connection.sendall(data)
                connection.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        threading.Thread(target=upstream, daemon=True).start()
        while True:
            data = connection.recv(65536)
            if not data:
                break
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3

import argparse
import logging
import socket
import ssl
import _thread

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UDPdotProxy:

    def __init__(self):
        self.args = self.get_arguments()

    def get_tcp_query(self, request):
        """Take a UDP query and convert it in to a TCP query by adding a 2 byte
        integer which contains the length of data that follows

        :param request: The request received on the UDP listener
        :type request: bytes
        :return: The request ready to send to the TCP server
        :rtype: bytes
        """

        message = b"\x00" + bytes(chr(len(request)), encoding='utf-8') + request
        return message

    def send_tcp(self, query):
        """Take the query and send it to the DNS over TLS server

        :param query: The data recieved on the TCP listener
        :type query: bytes
        :return: The response from the DNS over TLS server
        :rtype: bytes
        """

        server = (self.args.IP, 853)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        wrapped_socket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
        wrapped_socket.connect(server)

        tcp_query = self.get_tcp_query(query)
        wrapped_socket.send(tcp_query)
        data = wrapped_socket.recv(1024)

        return data

    def udp_handler(self, data, addr, socket):
        """Pass and receive the data to/from the TLS method

        :param data: The DNS request
        :type data: bytes
        :param addr: The IP Address and Port to send the response back to
        :type addr: Tuple
        :param socket: The socket object to use to send it back with
        :type socket: socket.socket
        """

        answer = self.send_tcp(data)
        if answer:
            udp_answer = answer[2:]
            socket.sendto(udp_answer, addr)
        else:
            logger.error("Invalid DNS query!")

    def main(self):
        """Create the UDP listener and thread it"""

        try:
            # Listen on UDP
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.bind((self.args.L_IP, self.args.L_PORT))

            while True:
                # Get data from the UDP listener and pass to a threaded handler
                udp_data, udp_addr = udp_sock.recvfrom(1024)
                _thread.start_new_thread(
                    self.udp_handler,
                    (udp_data, udp_addr, udp_sock)
                )

        except Exception as e:
            logger.error(str(e))
            udp_sock.close()

    def get_arguments(self):
        """Get the arguments and set some defaults

        :return: The parsed arguments
        :rtype: argparse.Namespace
        """

        args = argparse.ArgumentParser(
            'Run a local DNS proxy which will do a DNS lookup over TLS'
        )

        args.add_argument(
            '-i', '--ip', dest='IP', type=str, default='1.1.1.1',
            help='The IP address to do the DoT lookup with'
        )
        args.add_argument(
            '-p', '--local-port', dest='L_PORT', type=int, default=53,
            help='The local port to listen on'
        )
        args.add_argument(
            '-l', '--local-ip', dest='L_IP', type=str, default='0.0.0.0',
            help='The local IP address to listen on'
        )

        return args.parse_args()


if __name__ == '__main__':
    lookup = UDPdotProxy()
    lookup.main()

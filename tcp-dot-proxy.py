#!/usr/bin/env python3

import argparse
import logging
import socket
import ssl
import _thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TCPdotProxy:

    def __init__(self):
        self.args = self.get_arguments()

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

        wrapped_socket.send(query)
        data = wrapped_socket.recv(1024)

        return data

    def tcp_handler(self, data, connection):
        """Pass and receive the data to/from the TLS method

        :param data: The DNS request
        :type data: bytes
        :param connection: TCP connection
        :type connection: socket.socket
        """

        answer = self.send_tcp(data)
        if answer:
            connection.send(answer)
            connection.close()
        else:
            logger.error("Invalid DNS query!")

    def main(self):
        """Create the TCP listener and thread it"""

        try:
            # Listen on TCP
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.bind((self.args.L_IP, self.args.L_PORT))
            tcp_sock.listen()

            while True:
                # Get data from the TCP listener and pass to a threaded handler
                tcp_conn = tcp_sock.accept()[0]
                tcp_data = tcp_conn.recv(1024)
                _thread.start_new_thread(self.tcp_handler, (tcp_data, tcp_conn))

        except Exception as e:
            logger.error(str(e))
            tcp_sock.close()

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
    lookup = TCPdotProxy()
    lookup.main()

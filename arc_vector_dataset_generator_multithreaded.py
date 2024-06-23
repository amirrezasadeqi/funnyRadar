#####################################################################################################
# This code snippets were a try for gathering the arc vector data set using multithreading and byte
# buffers. but for now I could not make it to work, since there was a lot of difficulties in handling
# data bytes like 0x0A and so on in python. I think python reinterprets the byte data somewhere in my
# code, or maybe this is just a bad representation of data in terminal. for now I don't have more time
# so I will use the other files to do this, but in future ... .

# another way for doing this was using hex strings. when we see data in wireshark, the 0x0A data is
# displayed correctly, just the same as the case we use the string for saving the incoming data and
# filling this string buffer with the string calculated by the hex function applied to the bytes object
# coming from the socket.recv(1024) function.
# a good reference of this way is below repository:
# https://github.com/tobadia/petGPS/tree/master

# Note that in my works I saw that when printing the byte data, the bytes that are equivalent to characters
# like \n or !, are displayed in the bytes object, like b'\xee\xff\xee\xff\x10!\n....'

# so let's go for now!

#####################################################################################################
import io
import socket
import struct
import threading
import time


class TcpClient(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        # self._data_buffer = b''
        self._data_buffer = io.BytesIO()
        # A list containing each arc message with its label. each message is a dictionary like this:
        # {
        #   "arc_message":
        #       {"azimuth": value, "elevation": value, "arc_data_length": value, "arc_data": []},
        #   "label":
        #       True/False
        # }
        self._dissected_messages = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect_to_server()
        self._request_arc_data()
        self._data_capture_thread = threading.Thread(target=self._capture_data)
        self._data_capture_thread.start()
        self._run_dissect_loop()
        return

    def _connect_to_server(self):
        self._socket.connect((self._host, self._port))
        print(f"Connected to the server at: {self._host}:{self._port}")
        return

    def _close_connection(self):
        self._socket.close()
        return

    def _capture_data(self):
        timeout_counter = 0
        timeout_threshold = 5
        dataBuffer = b''
        try:
            while True:
                data = self._socket.recv(1024)
                if not data:
                    timeout_counter += 1
                    if timeout_counter > timeout_threshold:
                        break
                    time.sleep(0.1)
                    continue
                timeout_counter = 0  # resetting the timeout counter
                # self._data_buffer += data
                #######################################################################################
                # idx = 0
                # while idx < len(data) - 11:
                #     h, i, t, l = struct.unpack("<IHcI", data[idx:idx+11])
                #     if h == struct.unpack("<I", b'\xEE\xFF\xEE\xFF'):
                #         print("NEW MESSAGE")
                #     else:
                #         idx += 1
                idx = 0
                dataBuffer += data
                print("############################################################################################")
                while idx < len(dataBuffer) - 11:
                    if dataBuffer[idx: idx + 4] == b'\xee\xff\xee\xff':
                        print(struct.unpack('<IHcI', dataBuffer[:11]))
                        idx += 11
                    else:
                        idx += 1
                dataBuffer = dataBuffer[idx:]
                print(f"index is : {idx} and length of data is : {len(dataBuffer)}")
                print("############################################################################################")
                #######################################################################################
                self._append_data_to_buffer(data)

        except KeyboardInterrupt:
            print(f"Stopping the connection by keyboard interrupt")
        except Exception as e:
            print(f"Exception occurred in reading from socket:\n{e}\n")
        finally:
            self._close_connection()
        return

    def _append_data_to_buffer(self, data):
        self._data_buffer.seek(self._data_buffer.getbuffer().nbytes)
        self._data_buffer.write(data)
        return

    def _request_arc_data(self):
        with open("arc_data_request.hex", 'rb') as file:
            arc_data_request = file.read()
        self._socket.sendall(arc_data_request)
        return

    def _dissect_data(self):
        idx = 0  # index of data buffer
        header_size, id_size, type_size, message_length_size = 4, 2, 1, 4
        # I think because of the mechanism(probably stack like mechanism) of send and receive, the data captured
        # from the interface buffer comes in little endian format(I mean FFEEFFEE received as EEFFEEFF). so to unpack
        # the data with struct module you must use the little endian format.
        header = b'\xEE\xFF\xEE\xFF'
        prefix_size = header_size + id_size + type_size + message_length_size
        # while idx < len(self._data_buffer) - prefix_size:
        while idx < len(self._data_buffer.getvalue()) - prefix_size:
            self._data_buffer.seek(idx)
            potential_prefix_data_view = memoryview(self._data_buffer.read(prefix_size))
            # h, i, t, l = struct.unpack('<IHcI', potential_prefix_data_view)
            # if self._data_buffer[idx:idx + header_size] == header:
            # if potential_prefix_data_view[idx:idx + header_size] == header:
            #     print("new message")
            # print(potential_prefix_data_view[idx + header_size + id_size: idx + header_size + id_size + 2].tobytes() == b'\x02%')
            # print(int( potential_prefix_data_view[idx + header_size + id_size + 1: idx + header_size + id_size + 1 + message_length_size].tobytes() ))
            # print(self._data_buffer[idx:idx + header_size])
            # print(self._data_buffer[idx + 6:idx + 7])
            # print(self._data_buffer[idx + header_size: idx + header_size + id_size])
            # print(self._data_buffer[idx + header_size + id_size])
            # else:  # move to the next until you reach to message header
            #     idx += 1
        return

    def _run_dissect_loop(self):
        try:
            while True:
                # if len(self._data_buffer):
                if len(self._data_buffer.getvalue()):
                    self._dissect_data()
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print()
        except Exception as e:
            print(f"{e}")
        finally:
            print(f"save file and closing the resources!")
        return


if __name__ == '__main__':
    tcpClientObj = TcpClient(host="192.168.1.6", port=30031)
